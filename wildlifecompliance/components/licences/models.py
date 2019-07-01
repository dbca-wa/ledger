from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.contrib.postgres.fields.jsonb import JSONField
from django.db.models import Max
from django.db.models import Q
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

    ACTIVITY_PURPOSE_ACTION_REACTIVATE_RENEW = 'reactivate_renew'
    ACTIVITY_PURPOSE_ACTION_SURRENDER = 'surrender'
    ACTIVITY_PURPOSE_ACTION_CANCEL = 'cancel'
    ACTIVITY_PURPOSE_ACTION_SUSPEND = 'suspend'
    ACTIVITY_PURPOSE_ACTION_REINSTATE = 'reinstate'

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
        # only check if licence is the latest in its category for the applicant
        print('get_latest_activities_for_licence_activity_and_action in licence/models')
        if self.is_latest_in_category:
            latest_activities = self.latest_activities
            if licence_activity_id:
                latest_activities = latest_activities.filter(licence_activity_id=licence_activity_id)
            # get the list of can_<action> ApplicationSelectedActivity records
            if action:
                can_action_activity_ids = []
                purposes_in_open_applications = self.get_purposes_in_open_applications()
                for activity in latest_activities:
                    activity_can_action = activity.can_action(purposes_in_open_applications)
                    if action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_CANCEL:
                        if activity_can_action['can_cancel']:
                            can_action_activity_ids.append(activity.id)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SUSPEND:
                        if activity_can_action['can_suspend']:
                            can_action_activity_ids.append(activity.id)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SURRENDER:
                        if activity_can_action['can_surrender']:
                            can_action_activity_ids.append(activity.id)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REACTIVATE_RENEW:
                        if activity_can_action['can_reactivate_renew']:
                            can_action_activity_ids.append(activity.id)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REINSTATE:
                        if activity_can_action['can_reinstate']:
                            can_action_activity_ids.append(activity.id)
                latest_activities = latest_activities.filter(id__in=can_action_activity_ids)
        else:
            latest_activities = []
        return latest_activities

    def get_latest_purposes_for_licence_activity_and_action(self, licence_activity_id=None, action=None):
        """
        Return a list of LicencePurpose records for the licence
        Filter by licence_activity_id (optional) and/or specified action (optional)
        Exclude purposes that are currently in an application being processed
        """
        can_action_purpose_list = []
        purposes_in_open_applications_for_applicant = self.get_purposes_in_open_applications()
        for activity in self.get_latest_activities_for_licence_activity_and_action(licence_activity_id, action):
            for purpose in activity.purposes:
                if purpose.id not in purposes_in_open_applications_for_applicant:
                    can_action_purpose_list.append(purpose.id)
        return LicencePurpose.objects.filter(id__in=can_action_purpose_list).distinct()

    def get_purposes_in_open_applications(self):
        """
        Return a list of LicencePurpose records for the licence that are currently in an application being processed
        """
        from wildlifecompliance.components.applications.models import Application, ApplicationSelectedActivity

        open_applications = Application.objects.filter(
            Q(org_applicant=self.current_application.org_applicant)
            if self.current_application.org_applicant
            else Q(proxy_applicant=self.current_application.proxy_applicant)
            if self.current_application.proxy_applicant
            else Q(submitter=self.current_application.submitter, proxy_applicant=None, org_applicant=None)
        ).computed_filter(
            licence_category_id=self.licence_category.id
        ).exclude(
            selected_activities__processing_status__in=[
                ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED,
                ApplicationSelectedActivity.PROCESSING_STATUS_DECLINED,
                ApplicationSelectedActivity.PROCESSING_STATUS_DISCARDED
            ]
        )
        open_purposes = open_applications.values_list('licence_purposes', flat=True)
        return open_purposes

    @property
    def latest_activities_merged(self):
        """
        Return a list of activities for the licence, merged by licence_activity_id (1 per LicenceActivity)
        """
        latest_activities = self.latest_activities
        merged_activities = {}

        if self.is_latest_in_category:
            purposes_in_open_applications = self.get_purposes_in_open_applications()
        else:
            purposes_in_open_applications = None

        for activity in latest_activities:
            if self.is_latest_in_category:
                activity_can_action = activity.can_action(purposes_in_open_applications)
            else:
                activity_can_action = {
                    'licence_activity_id': activity.licence_activity_id,
                    'can_renew': False,
                    'can_amend': False,
                    'can_surrender': False,
                    'can_cancel': False,
                    'can_suspend': False,
                    'can_reissue': False,
                    'can_reinstate': False,
                }

            # Check if a record for the licence_activity_id already exists, if not, add
            if not merged_activities.get(activity.licence_activity_id):
                merged_activities[activity.licence_activity_id] = {
                    'licence_activity_id': activity.licence_activity_id,
                    'activity_name_str': activity.licence_activity.name,
                    'issue_date': activity.issue_date,
                    'start_date': activity.start_date,
                    'expiry_date': activity.expiry_date,
                    'activity_purpose_names_and_status': '\n'.join(['{} ({})'.format(
                        p.name, activity.get_activity_status_display())
                        for p in activity.purposes]),
                    'can_action':
                        {
                            'licence_activity_id': activity.licence_activity_id,
                            'can_renew': activity_can_action['can_renew'],
                            'can_amend': activity_can_action['can_amend'],
                            'can_surrender': activity_can_action['can_surrender'],
                            'can_cancel': activity_can_action['can_cancel'],
                            'can_suspend': activity_can_action['can_suspend'],
                            'can_reissue': activity_can_action['can_reissue'],
                            'can_reinstate': activity_can_action['can_reinstate'],
                        }
                }
            else:
                activity_key = merged_activities[activity.licence_activity_id]
                activity_key['activity_purpose_names_and_status'] += \
                    '\n' + '\n'.join(['{} ({})'.format(
                        p.name, activity.get_activity_status_display())
                        for p in activity.purposes])
                activity_key['can_action']['can_renew'] =\
                    activity_key['can_action']['can_renew'] or activity_can_action['can_renew']
                activity_key['can_action']['can_amend'] =\
                    activity_key['can_action']['can_amend'] or activity_can_action['can_amend']
                activity_key['can_action']['can_surrender'] =\
                    activity_key['can_action']['can_surrender'] or activity_can_action['can_surrender']
                activity_key['can_action']['can_cancel'] =\
                    activity_key['can_action']['can_cancel'] or activity_can_action['can_cancel']
                activity_key['can_action']['can_suspend'] =\
                    activity_key['can_action']['can_suspend'] or activity_can_action['can_suspend']
                activity_key['can_action']['can_reissue'] =\
                    activity_key['can_action']['can_reissue'] or activity_can_action['can_reissue']
                activity_key['can_action']['can_reinstate'] =\
                    activity_key['can_action']['can_reinstate'] or activity_can_action['can_reinstate']

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

    @property
    def is_latest_in_category(self):
        # Returns True if the licence is the most recent one of it's category, filtered by
        # matching org_applicant, proxy_applicant and submitter
        organisation_id = self.current_application.org_applicant
        proxy_id = self.current_application.proxy_applicant
        submitter = self.current_application.submitter
        return WildlifeLicence.objects.filter(
            Q(current_application__org_applicant_id=organisation_id) if organisation_id else
            (Q(current_application__submitter=proxy_id) |
                Q(current_application__proxy_applicant=proxy_id)) if proxy_id else
            Q(current_application__submitter=submitter,
              current_application__proxy_applicant=None,
              current_application__org_applicant=None
            )
        ).latest('id') == self

    @property
    def can_action(self):
        print('can_action in licences.models', self, self.current_application)
        # Returns DICT of can_<action> if any of the licence's latest_activities can be actioned
        can_action = {
            'can_amend': False,
            'can_renew': False,
            'can_reactivate_renew': False,
            'can_surrender': False,
            'can_cancel': False,
            'can_suspend': False,
            'can_reissue': False,
            'can_reinstate': False,
        }

        # only check if licence is the latest in its category for the applicant
        if self.is_latest_in_category:
            print('is latest in category, inside licence can_action')
            # set True if any activities can be actioned
            purposes_in_open_applications = self.get_purposes_in_open_applications()
            for activity in self.latest_activities:
                activity_can_action = activity.can_action(purposes_in_open_applications)
                if activity_can_action.get('can_amend'):
                    can_action['can_amend'] = True
                if activity_can_action.get('can_renew'):
                    can_action['can_renew'] = True
                if activity_can_action.get('can_reactivate_renew'):
                    can_action['can_reactivate_renew'] = True
                if activity_can_action.get('can_surrender'):
                    can_action['can_surrender'] = True
                if activity_can_action.get('can_cancel'):
                    can_action['can_cancel'] = True
                if activity_can_action.get('can_suspend'):
                    can_action['can_suspend'] = True
                if activity_can_action.get('can_reissue'):
                    can_action['can_reissue'] = True
                if activity_can_action.get('can_reinstate'):
                    can_action['can_reinstate'] = True

        return can_action

    def apply_action_to_licence(self, request, action):
        """
        Applies a specified action to a all of a licence's activities and purposes for a licence
        """
        if action not in [
            WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REACTIVATE_RENEW,
            WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SURRENDER,
            WildlifeLicence.ACTIVITY_PURPOSE_ACTION_CANCEL,
            WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SUSPEND,
            WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REINSTATE
        ]:
            raise ValidationError('Selected action is not valid')
        with transaction.atomic():
            for activity_id in self.latest_activities.values_list('licence_activity_id', flat=True):
                for activity in self.get_latest_activities_for_licence_activity_and_action(
                        activity_id, action):
                    if action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REACTIVATE_RENEW:
                        activity.reactivate_renew(request)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SURRENDER:
                        activity.surrender(request)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_CANCEL:
                        activity.cancel(request)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SUSPEND:
                        activity.suspend(request)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REINSTATE:
                        activity.reinstate(request)

    def apply_action_to_purposes(self, request, action):
        """
        Applies a specified action to a licence's purposes for a single licence_activity_id and selected purposes list
        If not all purposes for an activity are to be actioned, create new SYSTEM_GENERATED Applications and
        associated activities to apply the relevant statuses for each
        """
        from wildlifecompliance.components.applications.models import (
            Application, ApplicationSelectedActivity
        )
        if action not in [
            WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REACTIVATE_RENEW,
            WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SURRENDER,
            WildlifeLicence.ACTIVITY_PURPOSE_ACTION_CANCEL,
            WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SUSPEND,
            WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REINSTATE
        ]:
            raise ValidationError('Selected action is not valid')

        with transaction.atomic():

            purpose_ids_list = request.data.get('purpose_ids_list', None)
            purpose_ids_list = list(set(purpose_ids_list))
            purpose_ids_list.sort()

            if LicencePurpose.objects.filter(id__in=purpose_ids_list).\
                    values_list('licence_activity_id', flat=True).\
                    distinct().count() != 1:
                raise ValidationError(
                    'Selected purposes must all be of the same licence activity')

            licence_activity_id = LicencePurpose.objects.filter(id__in=purpose_ids_list). \
                first().licence_activity_id

            can_action_purposes = self.get_latest_purposes_for_licence_activity_and_action(
                licence_activity_id, action)
            can_action_purposes_ids_list = [purpose.id for purpose in can_action_purposes.order_by('id')]

            # if all purposes were selected by the user for action,
            # action all previous status ApplicationSelectedActivity records
            if purpose_ids_list == can_action_purposes_ids_list:
                activities_to_action = self.get_latest_activities_for_licence_activity_and_action(
                    licence_activity_id, action)
                # action target activities
                for activity in activities_to_action:
                    if action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REACTIVATE_RENEW:
                        activity.reactivate_renew(request)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SURRENDER:
                        activity.surrender(request)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_CANCEL:
                        activity.cancel(request)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SUSPEND:
                        activity.suspend(request)
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REINSTATE:
                        activity.reinstate(request)

            else:
                # else, if not all purposes were selected by the user for action:
                #  - if any ApplicationSelectedActivity records can be actioned completely (i.e. all purposes in the
                #        Application record are selected for action), action them
                #  - create new Application for the purposes to remain in previous status,
                #        using the first application found to have a purpose_id to remain in previous status
                #  - create new Application for the purposes to be actioned, using the first application found
                #        to have a purpose_id to action
                #  - add purposes from other relevant applications to either the new previous status
                #        or new actioned application copying data from their respective Applications
                #  - mark all previous status and not actioned ApplicationSelectedActivity records as REPLACED

                # Use dict for new_previous_status_applications, new application per previous possible status
                # e.g. REINSTATE can come from both CANCELLED and SURRENDERED activities/purposes
                new_previous_status_applications = {}
                new_actioned_application = None

                licence_latest_activities = self.get_latest_activities_for_licence_activity_and_action(
                    licence_activity_id, action)
                previous_statuses = list(set(licence_latest_activities.values_list('activity_status', flat=True)))
                for previous_status in previous_statuses:
                    new_previous_status_applications[previous_status] = None
                original_application_ids = licence_latest_activities.filter(
                    application__licence_purposes__in=purpose_ids_list).values_list('application_id', flat=True)
                original_applications = Application.objects.filter(id__in=original_application_ids)

                for application in original_applications:
                    # get purpose_ids linked with application
                    application_licence_purpose_ids_list = application.licence_purposes.filter(
                        licence_activity_id=licence_activity_id).values_list('id', flat=True)

                    activity = application.selected_activities.get(licence_activity_id=licence_activity_id)
                    # Get previous_status and target post_actioned_status
                    previous_status = activity.activity_status
                    if action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REACTIVATE_RENEW:
                        post_actioned_status = ApplicationSelectedActivity.ACTIVITY_STATUS_EXPIRED
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SURRENDER:
                        post_actioned_status = ApplicationSelectedActivity.ACTIVITY_STATUS_SURRENDERED
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_CANCEL:
                        post_actioned_status = ApplicationSelectedActivity.ACTIVITY_STATUS_CANCELLED
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SUSPEND:
                        post_actioned_status = ApplicationSelectedActivity.ACTIVITY_STATUS_SUSPENDED
                    elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REINSTATE:
                        post_actioned_status = ApplicationSelectedActivity.ACTIVITY_STATUS_CURRENT

                    # if an application's purpose_ids are all in the purpose_ids_list,
                    # completely action the ApplicationSelectedActivity
                    if not set(application_licence_purpose_ids_list) - set(purpose_ids_list):
                        if action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REACTIVATE_RENEW:
                            activity.reactivate_renew(request)
                        elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SURRENDER:
                            activity.surrender(request)
                        elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_CANCEL:
                            activity.cancel(request)
                        elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_SUSPEND:
                            activity.suspend(request)
                        elif action == WildlifeLicence.ACTIVITY_PURPOSE_ACTION_REINSTATE:
                            activity.reinstate(request)

                    # if application still has previous_status purposes after actioning selected purposes
                    elif set(application_licence_purpose_ids_list) - set(purpose_ids_list):
                        common_actioned_purpose_ids = set(application_licence_purpose_ids_list) & set(purpose_ids_list)
                        remaining_previous_status_purpose_ids = set(application_licence_purpose_ids_list) - set(purpose_ids_list)

                        # create new previous_status application from this application if not yet exists
                        if not new_previous_status_applications[previous_status]:
                            new_previous_status_applications[previous_status] = application.copy_application_purposes_for_status(
                                remaining_previous_status_purpose_ids, previous_status)
                        # else, if new previous_status application exists, link the target LicencePurpose IDs to it
                        else:
                            # Link the target LicencePurpose IDs to the application
                            for licence_purpose_id in remaining_previous_status_purpose_ids:
                                application.copy_application_purpose_to_target_application(
                                    new_previous_status_applications[previous_status],
                                    licence_purpose_id)

                        # create new actioned application from this application if not yet exists
                        if not new_actioned_application:
                            new_actioned_application = application.copy_application_purposes_for_status(
                                common_actioned_purpose_ids, post_actioned_status)
                        # else, if new actioned application exists, link the target LicencePurpose IDs to it
                        else:
                            # Link the target LicencePurpose IDs to the application
                            for licence_purpose_id in common_actioned_purpose_ids:
                                application.copy_application_purpose_to_target_application(
                                    new_actioned_application,
                                    licence_purpose_id)

                # Set original activities to REPLACED except for any that were ACTIONED completely
                original_activities = ApplicationSelectedActivity.objects.\
                    filter(application__id__in=original_application_ids).\
                    exclude(activity_status=post_actioned_status)
                for activity in original_activities:
                    activity.mark_as_replaced(request)

    @property
    def purposes_available_to_add(self):
        """
        Returns a list of LicencePurpose objects that can be added to a WildlifeLicence
        Same logic as the UserAvailableWildlifeLicencePurposesViewSet list function (used in API call)
        """
        available_purpose_records = LicencePurpose.objects.all()
        licence_category_id = self.licence_category.id
        current_activities = self.current_activities

        # Exclude any purposes that are linked with CURRENT activities
        active_purpose_ids = []
        for current_activity in current_activities:
            active_purpose_ids.extend([purpose.id for purpose in current_activity.purposes])
        available_purpose_records = available_purpose_records.exclude(
            id__in=active_purpose_ids
        )

        # Filter by Licence Category ID
        available_purpose_records = available_purpose_records.filter(
            licence_category_id=licence_category_id
        )

        return available_purpose_records

    @property
    def can_add_purpose(self):
        return self.is_latest_in_category and self.purposes_available_to_add.count() > 0


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
