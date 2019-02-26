import importlib
import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group, ContentType, Permission


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
    def default_permissions(cls):
        """
        Collects up all of the custom permission configurations from the app_dir/permissions.py
        modules for each app in INSTALLED_APPS and returns a dictionary of the
        form:
            permission_name: {permission_spec}
        """
        permissions = {}

        for app, module in cls.iter_app_configs():
            module_permissions = getattr(module, cls.PERMISSION_KEY, {})

            if module_permissions:
                # Detect duplicate permissions
                for permission_name in module_permissions:
                    if permission_name in permissions:
                        raise RuntimeError('Two permissions created with the ' +
                                           'same name: {}'.format(permission_name))
                permissions.update(module_permissions)

        return permissions


class CustomPermissionCollector(PermissionCollector):

    PERMISSION_KEY = 'CUSTOM_GROUP_PERMISSIONS'

    def get_or_create_models(self):
        """
        A mapping of permission name to permission instance. If the permission does not exist, it is created.
        """
        default_permissions = self.default_permissions()
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
