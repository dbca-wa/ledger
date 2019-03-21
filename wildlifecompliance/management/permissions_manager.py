import importlib
import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group, ContentType, Permission
from django.db import transaction
from ledger.accounts.utils import get_app_label
from wildlifecompliance.components.licences.models import LicenceActivity
from wildlifecompliance.components.applications.models import ActivityPermissionGroup

logger = logging.getLogger(__name__)


class PermissionCollector(object):

    MODULE_NAME = 'permissions'

    @classmethod
    def iter_app_configs(cls):
        for app in settings.INSTALLED_APPS:
            try:
                module = importlib.import_module('%s.%s' % (app, cls.MODULE_NAME))
            except ImportError:
                continue

            yield app, module

    @classmethod
    def default_objects(cls):
        """
        Collects up all of the custom configurations from the app_dir/permissions.py
        modules for each app in INSTALLED_APPS and returns a dictionary of the
        form:
            object_name: {object_spec}
        """
        collected_objects = {}

        for app, module in cls.iter_app_configs():
            module_objects = getattr(module, cls.COLLECTION_SOURCE, {})
            # Detect and exclude duplicate names
            if module_objects:
                for obj in module_objects:
                    object_name = obj['name'] if type(obj) == dict else obj
                    obj_data = obj if type(obj) == dict else module_objects[obj]
                    if object_name in collected_objects:
                        raise RuntimeError('Two {} created with the ' +
                                           'same name: {}'.format(cls.COLLECTION_SOURCE, object_name))
                    collected_objects[object_name] = obj_data

        return collected_objects


class CustomPermissionCollector(PermissionCollector):

    COLLECTION_SOURCE = 'CUSTOM_GROUP_PERMISSIONS'

    def get_or_create_models(self):
        """
        A mapping of permission name to permission instance. If the permission does not exist, it is created.
        """
        default_permissions = self.default_objects()
        actual = {}

        for permission_name, config in default_permissions.items():

            try:
                content_type = ContentType.objects.get(
                    model=config['model'],
                    app_label=config['app_label'],
                )
            except ObjectDoesNotExist:
                logger.error("Content Type {app_label} - {model} not found for permission: {codename}".format(
                    app_label=config['app_label'],
                    model=config['model'],
                    codename=permission_name,
                ))
                continue

            permission, created = Permission.objects.get_or_create(
                name=config['name'],
                content_type_id=content_type.id,
                codename=permission_name
            )
            if created:
                logger.info("Created custom permission: %s" % (permission_name))

            # Only assign permissions to default groups if they didn't exist in the database before.
            # Don't re-add permissions that were revoked by admins manually!
            if 'default_groups' in config and created:
                for group_name in config['default_groups']:
                    try:
                        group = Group.objects.get(name=group_name)
                    except ObjectDoesNotExist:
                        logger.error("Cannot assign permission {permission_name} to a non-existent group: {group}".format(
                            permission_name=permission_name,
                            group=group_name
                        ))
                        continue

                    group.permissions.add(permission)
                    logger.info("Assigned permission {permission_name} to group: {group}".format(
                        permission_name=permission_name,
                        group=group_name
                    ))

            actual[permission_name] = permission

        return actual


class CustomGroupCollector(PermissionCollector):

    COLLECTION_SOURCE = 'PERMISSION_GROUPS'

    def get_or_create_group(self, group_name, config):
        created = None
        if settings.GROUP_PREFIX and settings.GROUP_PREFIX not in group_name:
            group_name = "{prefix} - {name}".format(
                prefix=settings.GROUP_PREFIX,
                name=group_name
            )
        group = ActivityPermissionGroup.objects.filter(name=group_name).first()
        if not group:
            base_group = Group.objects.filter(name=group_name).first()
            if base_group:
                group = created = ActivityPermissionGroup.objects.create(
                    group_ptr_id=base_group.id,
                    name=base_group.name
                )
            else:
                group = created = ActivityPermissionGroup.objects.create(name=group_name)

        if created:
            logger.info("Created custom group: %s" % (group_name))

        if config['permissions'] and created:
            for permission_codename in config['permissions']:
                try:
                    permission = Permission.objects.get(
                        codename=permission_codename
                    )

                    group.permissions.add(permission)
                    logger.info("Assigned permission {permission_name} to group: {group}".format(
                        permission_name=permission_codename,
                        group=group_name
                    ))
                except ObjectDoesNotExist:
                    logger.error("Cannot assign non-existent permission {permission_name} to: {group}".format(
                        permission_name=permission_codename,
                        group=group_name
                    ))
                    raise 

        return group

    def get_or_create_models(self):
        """
        A mapping of group name to group instance. If the group does not exist, it is created.
        """
        default_groups = self.default_objects()
        actual = {}

        for group_name, config in default_groups.items():

            if config['per_activity']:
                for activity in LicenceActivity.objects.all():
                    activity_group_name = "{}: {}".format(group_name, activity.name)
                    group = self.get_or_create_group(activity_group_name, config)
                    group.licence_activities.add(activity)
            else:
                group = self.get_or_create_group(group_name, config)

        return actual


class CollectorManager(object):

    def __init__(self):
        if not get_app_label():
            raise Exception("SYSTEM_APP_LABEL is missing from settings.py or is blank!\
            \nPlease set it to the global app_label of the current system (e.g. 'wildlifecompliance').")
        with transaction.atomic():
            logger.info("Verifying presence of custom group permissions in the database...")
            CustomPermissionCollector().get_or_create_models()
            logger.info("Verifying presence of custom groups in the database...")
            CustomGroupCollector().get_or_create_models()
            logger.info("Finished collecting custom groups and permissions.")
