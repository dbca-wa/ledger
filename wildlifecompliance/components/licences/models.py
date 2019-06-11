from __future__ import unicode_literals

from django.db import models, transaction
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.contrib.postgres.fields.jsonb import JSONField
from django.db.models import Max
from ledger.accounts.models import EmailUser
from ledger.licence.models import LicenceType
from wildlifecompliance.components.main.models import (
    CommunicationsLogEntry,
    UserAction,
    Document
)


def update_licence_doc_filename(instance, filename):
    return 'wildlifecompliance/licences/{}/documents/{}'.format(
        instance.id, filename)


class LicenceDocument(Document):
    _file = models.FileField(upload_to=update_licence_doc_filename)

    class Meta:
        app_label = 'wildlifecompliance'


class LicencePurpose(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=30, default='')
    code = models.CharField(max_length=4, default='')
    schema = JSONField(default=list)
    base_application_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default='0')
    base_licence_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default='0')
    fields = JSONField(default=list)
    licence_category = models.ForeignKey(
        'LicenceCategory',
        blank=True,
        null=True
    )
    licence_activity = models.ForeignKey(
        'LicenceActivity',
        blank=True,
        null=True
    )

    # application_schema = JSONField(blank=True, null=True)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'Licence purpose'
        verbose_name_plural = 'Licence purposes'

    def __str__(self):
        return self.name

    @staticmethod
    def get_first_record(activity_name):
        # Use filter -> first() in case of records with duplicate names (e.g. "Bioprospecting licence")
        return LicencePurpose.objects.filter(name=activity_name).first()


class LicenceActivity(models.Model):
    name = models.CharField(max_length=100)
    licence_category = models.ForeignKey(
        'LicenceCategory',
        blank=True,
        null=True
    )
    purpose = models.ManyToManyField(
        LicencePurpose,
        blank=True,
        through='DefaultPurpose',
        related_name='wildlifecompliance_activity')
    short_name = models.CharField(max_length=30, default='')
    not_for_organisation = models.BooleanField(
        default=False,
        help_text='If ticked, this licenced activity will not be available for applications on behalf of an organisation.')
    schema = JSONField(default=list)
    # default_condition = models.ManyToManyField(Condition, through='DefaultCondition',blank= True)
    # default_period = models.PositiveIntegerField('Default Licence Period (days)', blank = True, null = True)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'Licenced activity'
        verbose_name_plural = 'Licenced activities'

    def __str__(self):
        return self.name


# class DefaultCondition(models.Model):
#     condition = models.ForeignKey(Condition)
#     wildlife_licence_activity = models.ForeignKey(LicencePurpose)
#     order = models.IntegerField()


# #LicenceType
class LicenceCategory(LicenceType):
    activity = models.ManyToManyField(
        LicenceActivity,
        blank=True,
        through='DefaultActivity',
        related_name='wildlifecompliance_activities')

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'Licence category'
        verbose_name_plural = 'Licence categories'

    @property
    # override LicenceType display_name to display name first instead of
    # short_name
    def display_name(self):
        result = self.name or self.short_name
        if self.replaced_by is None:
            return result
        else:
            return '{} (V{})'.format(result, self.version)


class DefaultActivity(models.Model):
    activity = models.ForeignKey(LicenceActivity)
    licence_category = models.ForeignKey(LicenceCategory)

    class Meta:
        unique_together = (('licence_category', 'activity'))
        app_label = 'wildlifecompliance'
        verbose_name = 'Licenced category - licenced activity mapping'
        verbose_name_plural = 'Licenced category - licenced activity mappings'

    def __str__(self):
        return '{} - {}'.format(self.licence_category, self.activity)


class DefaultPurpose(models.Model):
    purpose = models.ForeignKey(LicencePurpose)
    activity = models.ForeignKey(LicenceActivity)

    class Meta:
        unique_together = (('activity', 'purpose'))
        app_label = 'wildlifecompliance'
        verbose_name = 'Licenced activity - purpose mapping'
        verbose_name_plural = 'Licenced activity - purpose mappings'

    def __str__(self):
        return '{} - {}'.format(self.activity, self.purpose)


class WildlifeLicence(models.Model):
    licence_document = models.ForeignKey(
        LicenceDocument,
        blank=True,
        null=True,
        related_name='licence_document')
    replaced_by = models.ForeignKey('self', blank=True, null=True)
    extracted_fields = JSONField(blank=True, null=True)
    licence_number = models.CharField(max_length=64, blank=True, null=True)
    licence_sequence = models.IntegerField(blank=True, default=1)
    licence_category = models.ForeignKey(LicenceCategory)
    current_application = models.ForeignKey('wildlifecompliance.Application')

    class Meta:
        unique_together = (
            ('licence_number',
             'licence_sequence',
             'licence_category'))
        app_label = 'wildlifecompliance'

    def __str__(self):
        return '{} {}-{}'.format(self.licence_category, self.licence_number, self.licence_sequence)

    def save(self, *args, **kwargs):
        super(WildlifeLicence, self).save(*args, **kwargs)
        if not self.licence_number:
            self.licence_number = 'L{0:06d}'.format(
                self.next_licence_number_id)
            self.save()

    def get_activities_by_activity_status(self, status):
        return self.current_application.get_activity_chain(activity_status=status).order_by(
            'licence_activity_id', '-issue_date'
        )

    def get_activities_by_processing_status(self, status):
        return self.current_application.get_activity_chain(processing_status=status).order_by(
            'licence_activity_id', '-issue_date'
        )

    def get_latest_activities_for_licence_activity_and_action(self, licence_activity_id=None, action=None):
        '''
        Return a list of ApplicationSelectedActivity records for the licence
        Filter by licence_activity_id (optional) and/or specified action (optional)
        '''
        # for a given licence_activity_id and action, return relevant applications
        activities = self.latest_activities
        if licence_activity_id:
            activities = activities.filter(licence_activity_id=licence_activity_id)
        # get the list of can_<action> ApplicationSelectedActivity records
        if action:
            can_action_asa_ids = []
            if action == 'cancel':
                can_action_asa_ids = [asa.id for asa in activities if asa.can_cancel]
            elif action == 'suspend':
                can_action_asa_ids = [asa.id for asa in activities if asa.can_suspend]
            elif action == 'surrender':
                can_action_asa_ids = [asa.id for asa in activities if asa.can_surrender]
            activities = activities.filter(id__in=can_action_asa_ids)
        return activities

    def get_latest_purposes_for_licence_activity_and_action(self, licence_activity_id=None, action=None):
        '''
        Return a list of LicencePurpose records for the licence
        Filter by licence_activity_id (optional) and/or specified action (optional)
        '''
        can_action_purpose_list = []
        for activity in self.get_latest_activities_for_licence_activity_and_action(licence_activity_id, action):
            for purpose in activity.purposes:
                can_action_purpose_list.append(purpose.id)
        return LicencePurpose.objects.filter(id__in=can_action_purpose_list).distinct()

    @property
    def latest_activities_merged(self):
        from wildlifecompliance.components.applications.models import ApplicationSelectedActivity
        latest_activities = self.get_activities_by_processing_status(ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED) \
            .exclude(activity_status=ApplicationSelectedActivity.ACTIVITY_STATUS_REPLACED)
        # licence_activity_ids = latest_activities.values_list('licence_activity_id', flat=True).distinct()
        merged_activities = {}
        # for licence_activity_id in licence_activity_ids:
        #     # Check if a record for the licence_activity_id already exists, if not, add
        #     if not merged_activities.get(licence_activity_id):
        #         activities = latest_activities.filter(licence_activity_id=licence_activity_id)
        for activity in latest_activities:
            # Check if a record for the licence_activity_id already exists, if not, add
            if not merged_activities.get(activity.licence_activity_id):
                merged_activities[activity.licence_activity_id] = {
                    'activity_name_str': activity.licence_activity.name,
                    'issue_date': activity.issue_date,
                    'start_date': activity.start_date,
                    'expiry_date': activity.expiry_date,
                    'activity_purpose_names_and_status': '\n'.join(['{} ({})'.format(
                        p.short_name, activity.get_activity_status_display())
                        for p in activity.purposes]),
                    'can_renew': activity.can_renew,
                    'can_amend': activity.can_amend,
                    'can_surrender': activity.can_surrender,
                    'can_cancel': activity.can_cancel,
                    'can_suspend': activity.can_suspend,
                    'can_reissue': activity.can_reissue,
                    'can_reinstate': activity.can_reinstate,
                }
            else:
                activity_key = merged_activities[activity.licence_activity_id]
                activity_key['activity_purpose_names_and_status'] +=  \
                    '\n' + '\n'.join(['{} ({})'.format(
                        p.short_name, activity.get_activity_status_display())
                        for p in activity.purposes])
                activity_key['can_renew'] = activity_key['can_renew'] or activity.can_renew
                activity_key['can_amend'] = activity_key['can_amend'] or activity.can_amend
                activity_key['can_surrender'] = activity_key['can_surrender'] or activity.can_surrender
                activity_key['can_cancel'] = activity_key['can_cancel'] or activity.can_cancel
                activity_key['can_suspend'] = activity_key['can_suspend'] or activity.can_suspend
                activity_key['can_reissue'] = activity_key['can_reissue'] or activity.can_reissue
                activity_key['can_reinstate'] = activity_key['can_reinstate'] or activity.can_reinstate

        merged_activities_list = merged_activities.values()

        return merged_activities_list

    @property
    def latest_activities(self):
        from wildlifecompliance.components.applications.models import ApplicationSelectedActivity
        return self.get_activities_by_processing_status(ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED)\
            .exclude(activity_status=ApplicationSelectedActivity.ACTIVITY_STATUS_REPLACED)

    @property
    def current_activities(self):
        from wildlifecompliance.components.applications.models import ApplicationSelectedActivity
        return self.get_activities_by_activity_status(ApplicationSelectedActivity.ACTIVITY_STATUS_CURRENT)

    @property
    def next_licence_number_id(self):
        licence_number_max = WildlifeLicence.objects.all().aggregate(
            Max('licence_number'))['licence_number__max']
        if licence_number_max is None:
            return self.pk
        else:
            return int(licence_number_max.split('L')[1]) + 1

    @property
    def reference(self):
        return '{}-{}'.format(self.licence_number, self.licence_sequence)

    @property
    def is_issued(self):
        return self.licence_number is not None and len(self.licence_number) > 0

    def cancel_purposes(self, request):
        '''
        Cancels a licence's purposes for a selected licence_activity_id and purposes list
        '''
        from wildlifecompliance.components.applications.models import (
            Application, ApplicationSelectedActivity, ApplicationFormDataRecord
        )
        purpose_ids_list = request.data.get('purpose_ids_list', None)
        purpose_ids_list = list(set(purpose_ids_list))
        purpose_ids_list.sort()
        licence_activity_id = LicencePurpose.objects.filter(id__in=purpose_ids_list). \
            first().licence_activity_id
        can_cancel_purposes = self.get_latest_purposes_for_licence_activity_and_action(licence_activity_id, 'cancel')
        can_cancel_purposes_ids_list = [purpose.id for purpose in can_cancel_purposes.order_by('id')]

        # if all purposes were selected by the user for cancel, cancel all current ApplicationSelectedActivity records
        if purpose_ids_list == can_cancel_purposes_ids_list:
            activities_to_cancel = self.get_latest_activities_for_licence_activity_and_action(
                licence_activity_id, 'cancel')
            with transaction.atomic():
                # cancel target activities
                for activity in activities_to_cancel:
                    activity.cancel(request)

        # else, if not all purposes were selected by the user for cancel:
        #  - if any ApplicationSelectedActivity records can be cancelled completely (i.e. all purposes in the
        #        Application record are selected for cancel), cancel them
        #  - create new Application for the purposes to remain current, using the first application found
        #        to have a purpose_id to remain current
        #  - create new Application for the purposes to be cancelled, using the first application found
        #        to have a purpose_id to cancel
        #  - add purposes from other relevant applications to either the new current or new cancelled application,
        #        copying data from their respective Applications
        #  - mark all previously current and not cancelled ApplicationSelectedActivity records as REPLACED
        else:
            new_current_application = None
            new_cancelled_application = None

            licence_latest_activities = self.get_latest_activities_for_licence_activity_and_action(
                licence_activity_id, 'cancel')
            original_application_ids = licence_latest_activities.filter(
                application__licence_purposes__in=purpose_ids_list).values_list('application_id', flat=True)
            original_applications = Application.objects.filter(id__in=original_application_ids)
            with transaction.atomic():
                for application in original_applications:
                    # get purpose_ids linked with application
                    application_licence_purpose_ids_list = application.licence_purposes.filter(
                        licence_activity_id=licence_activity_id).values_list('id', flat=True)

                    # if application's purpose_ids are all listed in the purpose_ids_list,
                    # completely cancel ApplicationSelectedActivity
                    if not set(application_licence_purpose_ids_list) - set(purpose_ids_list):
                        activity = application.selected_activities.get(licence_activity_id=licence_activity_id)
                        activity.cancel(request)

                    # if application still has current purposes after cancelling selected purposes
                    if set(application_licence_purpose_ids_list) - set(purpose_ids_list):
                        common_cancelled_purpose_ids = set(application_licence_purpose_ids_list) & set(purpose_ids_list)
                        remaining_current_purpose_ids = set(application_licence_purpose_ids_list) - set(purpose_ids_list)

                        # create new current application from this application if not exists
                        if not new_current_application:
                            new_current_application = application.copy_application_purposes_for_status(
                                remaining_current_purpose_ids, ApplicationSelectedActivity.ACTIVITY_STATUS_CURRENT)
                        # else, if new current application exists, link the target LicencePurpose IDs to it
                        else:
                            # Link the target LicencePurpose IDs to the application
                            for licence_purpose_id in remaining_current_purpose_ids:
                                application.copy_application_purpose_to_target_application(
                                    new_current_application,
                                    licence_purpose_id)

                        # create new cancelled application from this application if not exists
                        if not new_cancelled_application:
                            new_cancelled_application = application.copy_application_purposes_for_status(
                                common_cancelled_purpose_ids, ApplicationSelectedActivity.ACTIVITY_STATUS_CANCELLED)
                        # else, if new cancelled application exists, link the target LicencePurpose IDs to it
                        else:
                            # Link the target LicencePurpose IDs to the application
                            for licence_purpose_id in common_cancelled_purpose_ids:
                                application.copy_application_purpose_to_target_application(
                                    new_cancelled_application,
                                    licence_purpose_id)

                # Set original activities to REPLACED except for any that were CANCELLED completely
                original_activities = ApplicationSelectedActivity.objects.\
                    filter(application__id__in=original_application_ids).\
                    exclude(activity_status=ApplicationSelectedActivity.ACTIVITY_STATUS_CANCELLED)
                for activity in original_activities:
                    activity.mark_as_replaced(request)

    def generate_doc(self):
        from wildlifecompliance.components.licences.pdf import create_licence_doc
        self.licence_document = create_licence_doc(
            self, self.current_application)
        self.save()

    def log_user_action(self, action, request):
        return LicenceUserAction.log_action(self, action, request.user)


class LicenceLogEntry(CommunicationsLogEntry):
    licence = models.ForeignKey(WildlifeLicence, related_name='comms_logs')

    class Meta:
        app_label = 'wildlifecompliance'

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.licence.id
        super(LicenceLogEntry, self).save(**kwargs)


class LicenceUserAction(UserAction):
    ACTION_CREATE_LICENCE = "Create licence {}"
    ACTION_UPDATE_LICENCE = "Create licence {}"

    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, licence, action, user):
        return cls.objects.create(
            licence=licence,
            who=user,
            what=str(action)
        )

    licence = models.ForeignKey(WildlifeLicence, related_name='action_logs')


# @receiver(pre_delete, sender=WildlifeLicence)
# def delete_documents(sender, instance, *args, **kwargs):
#     for document in instance.documents.all():
#         document.delete()
