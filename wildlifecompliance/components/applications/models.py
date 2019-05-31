from __future__ import unicode_literals

import datetime
import logging
import six
import re
from decimal import Decimal
from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.db.models.query import QuerySet
from django.dispatch import receiver
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.payments.invoice.models import Invoice
from ledger.checkout.utils import calculate_excl_gst
from wildlifecompliance.components.main.utils import (
    checkout, set_session_application,
    delete_session_application,
    flush_checkout_session
)

from wildlifecompliance.components.organisations.models import Organisation
from wildlifecompliance.components.organisations.emails import send_org_id_update_request_notification
from wildlifecompliance.components.main.models import CommunicationsLogEntry, UserAction, Document
from wildlifecompliance.components.applications.email import (
    send_application_submitter_email_notification,
    send_application_submit_email_notification,
    send_assessment_email_notification,
    send_assessment_reminder_email,
    send_amendment_submit_email_notification,
    send_application_issue_notification,
    send_application_decline_notification,
    send_id_update_request_notification,
    send_application_return_to_officer_conditions_notification,
    send_activity_invoice_email_notification,
)
from wildlifecompliance.components.main.utils import get_choice_value
from wildlifecompliance.ordered_model import OrderedModel
from wildlifecompliance.components.licences.models import LicenceCategory, LicenceActivity

logger = logging.getLogger(__name__)


def update_application_doc_filename(instance, filename):
    return 'wildlifecompliance/applications/{}/documents/{}'.format(
        instance.application.id, filename)


def update_pdf_licence_filename(instance, filename):
    return 'wildlifecompliance/applications/{}/wildlife_compliance_licence/{}'.format(instance.id, filename)


def update_assessment_inspection_report_filename(instance, filename):
    return 'wildlifecompliance/assessments/{}/inspection_report/{}'.format(instance.id, filename)


def replace_special_chars(input_str, new_char='_'):
    return re.sub('[^A-Za-z0-9]+', new_char, input_str).strip('_').lower()


def update_application_comms_log_filename(instance, filename):
    return 'wildlifecompliance/applications/{}/communications/{}/{}'.format(
        instance.log_entry.application.id, instance.id, filename)


class ActivityPermissionGroup(Group):
    licence_activities = models.ManyToManyField(
        'wildlifecompliance.LicenceActivity',
        blank=True)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'Activity permission group'
        verbose_name_plural = 'Activity permission groups'

    def __str__(self):
        return '{} ({} members)'.format(
            self.name,
            EmailUser.objects.filter(groups__name=self.name).count()
        )

    @property
    def display_name(self):
        return self.__str__

    @property
    def members(self):
        return EmailUser.objects.filter(
            groups__id=self.id
        ).distinct()

    @staticmethod
    def get_groups_for_activities(activities, codename):
        """
        Find matching ActivityPermissionGroups for a list of activities, activity ID or a LicenceActivity instance.
        :return: ActivityPermissionGroup QuerySet
        """
        from wildlifecompliance.components.licences.models import LicenceActivity

        if isinstance(activities, LicenceActivity):
            activities = [activities.id]

        groups = ActivityPermissionGroup.objects.filter(
            licence_activities__id__in=activities if isinstance(
                activities, (list, QuerySet)) else [activities]
        )
        if isinstance(codename, list):
            groups = groups.filter(permissions__codename__in=codename)
        else:
            groups = groups.filter(permissions__codename=codename)
        return groups.distinct()


class ApplicationDocument(Document):
    application = models.ForeignKey('Application', related_name='documents')
    _file = models.FileField(upload_to=update_application_doc_filename)
    input_name = models.CharField(max_length=255, null=True, blank=True)
    # after initial submit prevent document from being deleted
    can_delete = models.BooleanField(default=True)

    def delete(self):
        if self.can_delete:
            return super(ApplicationDocument, self).delete()
        logger.info(
            'Cannot delete existing document object after application has been submitted (including document submitted before\
            application pushback to status Draft): {}'.format(
                self.name)
        )

    class Meta:
        app_label = 'wildlifecompliance'


class Application(RevisionedMixin):

    APPLICANT_TYPE_ORGANISATION = 'ORG'
    APPLICANT_TYPE_PROXY = 'PRX'
    APPLICANT_TYPE_SUBMITTER = 'SUB'

    CUSTOMER_STATUS_DRAFT = 'draft'
    CUSTOMER_STATUS_UNDER_REVIEW = 'under_review'
    CUSTOMER_STATUS_AWAITING_PAYMENT = 'awaiting_payment'
    CUSTOMER_STATUS_AMENDMENT_REQUIRED = 'amendment_required'
    CUSTOMER_STATUS_ACCEPTED = 'accepted'
    CUSTOMER_STATUS_PARTIALLY_APPROVED = 'partially_approved'
    CUSTOMER_STATUS_DECLINED = 'declined'
    CUSTOMER_STATUS_CHOICES = (
        (CUSTOMER_STATUS_DRAFT, 'Draft'),
        (CUSTOMER_STATUS_AWAITING_PAYMENT, 'Awaiting Payment'),
        (CUSTOMER_STATUS_UNDER_REVIEW, 'Under Review'),
        (CUSTOMER_STATUS_AMENDMENT_REQUIRED, 'Amendment Required'),
        (CUSTOMER_STATUS_ACCEPTED, 'Accepted'),
        (CUSTOMER_STATUS_PARTIALLY_APPROVED, 'Partially Approved'),
        (CUSTOMER_STATUS_DECLINED, 'Declined'),
    )

    # List of statuses from above that allow a customer to edit an application.
    CUSTOMER_EDITABLE_STATE = [
        CUSTOMER_STATUS_DRAFT,
        CUSTOMER_STATUS_AWAITING_PAYMENT,
        CUSTOMER_STATUS_AMENDMENT_REQUIRED,
    ]

    PROCESSING_STATUS_DRAFT = 'draft'
    PROCESSING_STATUS_AWAITING_APPLICANT_RESPONSE = 'awaiting_applicant_response'
    PROCESSING_STATUS_APPROVED = 'approved'
    PROCESSING_STATUS_PARTIALLY_APPROVED = 'partially_approved'
    PROCESSING_STATUS_DECLINED = 'declined'
    PROCESSING_STATUS_DISCARDED = 'discarded'
    PROCESSING_STATUS_UNDER_REVIEW = 'under_review'
    PROCESSING_STATUS_CHOICES = (
        (PROCESSING_STATUS_DRAFT, 'Draft'),
        (PROCESSING_STATUS_AWAITING_APPLICANT_RESPONSE, 'Awaiting Applicant Response'),
        (PROCESSING_STATUS_APPROVED, 'Approved'),
        (PROCESSING_STATUS_PARTIALLY_APPROVED, 'Partially Approved'),
        (PROCESSING_STATUS_DECLINED, 'Declined'),
        (PROCESSING_STATUS_DISCARDED, 'Discarded'),
        (PROCESSING_STATUS_UNDER_REVIEW, 'Under Review'),
    )

    # List of statuses from above that allow a customer to view an application
    # (read-only)
    CUSTOMER_VIEWABLE_STATE = [
        PROCESSING_STATUS_UNDER_REVIEW,
        PROCESSING_STATUS_APPROVED,
        PROCESSING_STATUS_DECLINED,
        PROCESSING_STATUS_PARTIALLY_APPROVED,
    ]

    ID_CHECK_STATUS_NOT_CHECKED = 'not_checked'
    ID_CHECK_STATUS_AWAITING_UPDATE = 'awaiting_update'
    ID_CHECK_STATUS_UPDATED = 'updated'
    ID_CHECK_STATUS_ACCEPTED = 'accepted'
    ID_CHECK_STATUS_CHOICES = (
        (ID_CHECK_STATUS_NOT_CHECKED, 'Not Checked'),
        (ID_CHECK_STATUS_AWAITING_UPDATE, 'Awaiting Update'),
        (ID_CHECK_STATUS_UPDATED, 'Updated'),
        (ID_CHECK_STATUS_ACCEPTED, 'Accepted')
    )

    RETURN_CHECK_STATUS_NOT_CHECKED = 'not_checked'
    RETURN_CHECK_STATUS_AWAITING_RETURNS = 'awaiting_returns'
    RETURN_CHECK_STATUS_COMPLETED = 'completed'
    RETURN_CHECK_STATUS_ACCEPTED = 'accepted'
    RETURN_CHECK_STATUS_CHOICES = (
        (RETURN_CHECK_STATUS_NOT_CHECKED, 'Not Checked'),
        (RETURN_CHECK_STATUS_AWAITING_RETURNS, 'Awaiting Returns'),
        (RETURN_CHECK_STATUS_COMPLETED, 'Completed'),
        (RETURN_CHECK_STATUS_ACCEPTED, 'Accepted')
    )

    CHARACTER_CHECK_STATUS_NOT_CHECKED = 'not_checked'
    CHARACTER_CHECK_STATUS_ACCEPTED = 'accepted'
    CHARACTER_CHECK_STATUS_CHOICES = (
        (CHARACTER_CHECK_STATUS_NOT_CHECKED, 'Not Checked'),
        (CHARACTER_CHECK_STATUS_ACCEPTED, 'Accepted')
    )

    REVIEW_STATUS_NOT_REVIEWED = 'not_reviewed'
    REVIEW_STATUS_AWAITING_AMENDMENTS = 'awaiting_amendments'
    REVIEW_STATUS_AMENDED = 'amended'
    REVIEW_STATUS_ACCEPTED = 'accepted'
    REVIEW_STATUS_CHOICES = (
        (REVIEW_STATUS_NOT_REVIEWED, 'Not Reviewed'),
        (REVIEW_STATUS_AWAITING_AMENDMENTS, 'Awaiting Amendments'),
        (REVIEW_STATUS_AMENDED, 'Amended'),
        (REVIEW_STATUS_ACCEPTED, 'Accepted')
    )

    APPLICATION_TYPE_NEW_LICENCE = 'new_licence'
    APPLICATION_TYPE_ACTIVITY = 'new_activity'
    APPLICATION_TYPE_AMENDMENT = 'amend_activity'
    APPLICATION_TYPE_RENEWAL = 'renew_activity'
    APPLICATION_TYPE_CHOICES = (
        (APPLICATION_TYPE_NEW_LICENCE, 'New'),
        (APPLICATION_TYPE_ACTIVITY, 'New Activity'),
        (APPLICATION_TYPE_AMENDMENT, 'Amendment'),
        (APPLICATION_TYPE_RENEWAL, 'Renewal'),
    )

    application_type = models.CharField(
        'Application Type',
        max_length=40,
        choices=APPLICATION_TYPE_CHOICES,
        default=APPLICATION_TYPE_NEW_LICENCE)
    comment_data = JSONField(blank=True, null=True)
    licence_purposes = models.ManyToManyField(
        'wildlifecompliance.LicencePurpose',
        blank=True
    )
    customer_status = models.CharField(
        'Customer Status',
        max_length=40,
        choices=CUSTOMER_STATUS_CHOICES,
        default=CUSTOMER_STATUS_DRAFT)
    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    lodgement_date = models.DateTimeField(blank=True, null=True)
    org_applicant = models.ForeignKey(
        Organisation,
        blank=True,
        null=True,
        related_name='org_applications')
    proxy_applicant = models.ForeignKey(
        EmailUser,
        blank=True,
        null=True,
        related_name='wildlifecompliance_proxy')
    submitter = models.ForeignKey(
        EmailUser,
        blank=True,
        null=True,
        related_name='wildlifecompliance_applications')
    assigned_officer = models.ForeignKey(
        EmailUser,
        blank=True,
        null=True,
        related_name='wildlifecompliance_applications_assigned')
    id_check_status = models.CharField(
        'Identification Check Status',
        max_length=30,
        choices=ID_CHECK_STATUS_CHOICES,
        default=ID_CHECK_STATUS_NOT_CHECKED)
    return_check_status = models.CharField(
        'Return Check Status',
        max_length=30,
        choices=RETURN_CHECK_STATUS_CHOICES,
        default=RETURN_CHECK_STATUS_NOT_CHECKED)
    character_check_status = models.CharField(
        'Character Check Status',
        max_length=30,
        choices=CHARACTER_CHECK_STATUS_CHOICES,
        default=CHARACTER_CHECK_STATUS_NOT_CHECKED)
    review_status = models.CharField(
        'Review Status',
        max_length=30,
        choices=REVIEW_STATUS_CHOICES,
        default=REVIEW_STATUS_NOT_REVIEWED)
    licence = models.ForeignKey(
        'wildlifecompliance.WildlifeLicence',
        null=True,
        blank=True)
    previous_application = models.ForeignKey(
        'self', on_delete=models.PROTECT, blank=True, null=True)
    application_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default='0')

    class Meta:
        app_label = 'wildlifecompliance'

    def __str__(self):
        return str(self.id)

    # Append 'A' to Application id to generate Lodgement number. Lodgement
    # number and lodgement sequence are used to generate Reference.
    def save(self, *args, **kwargs):
        super(Application, self).save(*args, **kwargs)
        if self.lodgement_number == '':
            new_lodgement_id = 'A{0:06d}'.format(self.pk)
            self.lodgement_number = new_lodgement_id
            self.save()

    @property
    def applicant(self):
        if self.org_applicant:
            return self.org_applicant.organisation.name
        elif self.proxy_applicant:
            return "{} {}".format(
                self.proxy_applicant.first_name,
                self.proxy_applicant.last_name)
        else:
            return "{} {}".format(
                self.submitter.first_name,
                self.submitter.last_name)

    @property
    def applicant_details(self):
        if self.org_applicant:
            return '{} \n{}'.format(
                self.org_applicant.organisation.name,
                self.org_applicant.address)
        elif self.proxy_applicant:
            return "{} {}\n{}".format(
                self.proxy_applicant.first_name,
                self.proxy_applicant.last_name,
                self.proxy_applicant.addresses.all().first())
        else:
            return "{} {}\n{}".format(
                self.submitter.first_name,
                self.submitter.last_name,
                self.submitter.addresses.all().first())

    @property
    def applicant_id(self):
        if self.org_applicant:
            return self.org_applicant.id
        elif self.proxy_applicant:
            return self.proxy_applicant.id
        else:
            return self.submitter.id

    @property
    def applicant_type(self):
        if self.org_applicant:
            return self.APPLICANT_TYPE_ORGANISATION
        elif self.proxy_applicant:
            return self.APPLICANT_TYPE_PROXY
        else:
            return self.APPLICANT_TYPE_SUBMITTER

    @property
    def processing_status(self):
        selected_activities = self.selected_activities.all()
        activity_statuses = [activity.processing_status for activity in selected_activities]
        # not yet submitted
        if activity_statuses.count(ApplicationSelectedActivity.PROCESSING_STATUS_DRAFT) == len(activity_statuses):
            return self.PROCESSING_STATUS_DRAFT
        # application discarded
        elif activity_statuses.count(ApplicationSelectedActivity.PROCESSING_STATUS_DISCARDED) == len(activity_statuses):
            return self.PROCESSING_STATUS_DISCARDED
        # amendment request sent to user and outstanding
        elif self.active_amendment_requests.filter(status=AmendmentRequest.AMENDMENT_REQUEST_STATUS_REQUESTED).count() > 0:
            return self.PROCESSING_STATUS_AWAITING_APPLICANT_RESPONSE
        # all activities approved
        elif activity_statuses.count(ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED) == len(activity_statuses):
            return self.PROCESSING_STATUS_APPROVED
        # one or more (but not all) activities approved
        elif 0 < activity_statuses.count(ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED) < \
                len(activity_statuses):
            return self.PROCESSING_STATUS_PARTIALLY_APPROVED
        # all activities declined
        elif activity_statuses.count(ApplicationSelectedActivity.PROCESSING_STATUS_DECLINED) == len(activity_statuses):
            return self.PROCESSING_STATUS_DECLINED
        else:
            return self.PROCESSING_STATUS_UNDER_REVIEW

    @property
    def has_amendment(self):
        return self.active_amendment_requests.filter(status=AmendmentRequest.AMENDMENT_REQUEST_STATUS_REQUESTED).exists()

    @property
    def is_assigned(self):
        return self.assigned_officer is not None

    @property
    def can_user_edit(self):
        """
        :return: True if the application is in one of the editable status.
        """
        return self.customer_status in self.CUSTOMER_EDITABLE_STATE

    @property
    def can_user_view(self):
        """
        :return: True if the application is in one of the approved status.
        """
        return self.customer_status in self.CUSTOMER_VIEWABLE_STATE

    @property
    def is_discardable(self):
        """
        An application can be discarded by a customer if:
        1 - It is a draft or a draft awaiting payment
        2- or if the application has been pushed back to the user
        TODO: need to confirm regarding (2) here related to ApplicationSelectedActivity
        """
        return self.customer_status in [
            Application.CUSTOMER_STATUS_DRAFT,
            Application.CUSTOMER_STATUS_AWAITING_PAYMENT,
        ] or self.processing_status == Application.PROCESSING_STATUS_AWAITING_APPLICANT_RESPONSE

    @property
    def is_deletable(self):
        """
        An application can be deleted only if it is a draft and it hasn't been lodged yet
        :return:
        """
        return self.customer_status in [
            Application.CUSTOMER_STATUS_DRAFT,
            Application.CUSTOMER_STATUS_AWAITING_PAYMENT,
        ] and not self.lodgement_number

    @property
    def application_fee_paid(self):
        return self.payment_status in [
            Invoice.PAYMENT_STATUS_NOT_REQUIRED,
            Invoice.PAYMENT_STATUS_PAID,
            Invoice.PAYMENT_STATUS_OVERPAID,
        ]

    @property
    def payment_status(self):
        # TODO: needs more work, underpaid/overpaid statuses to be added, refactor to key/name like processing_status
        if self.application_fee == 0:
            return Invoice.PAYMENT_STATUS_NOT_REQUIRED
        else:
            if self.invoices.count() == 0:
                return Invoice.PAYMENT_STATUS_UNPAID
            else:
                try:
                    latest_invoice = Invoice.objects.get(
                        reference=self.invoices.latest('id').invoice_reference)
                except Invoice.DoesNotExist:
                    return Invoice.PAYMENT_STATUS_UNPAID
                return latest_invoice.payment_status

    @property
    def regions_list(self):
        return self.region.split(',') if self.region else []

    @property
    def permit(self):
        return self.licence.licence_document._file.url if self.licence else None

    @property
    def licence_officers(self):
        groups = self.get_permission_groups('licensing_officer').values_list('id', flat=True)
        return EmailUser.objects.filter(
            groups__id__in=groups
        ).distinct()

    @property
    def officers_and_assessors(self):
        groups = self.get_permission_groups(
            ['licensing_officer',
             'assessor',
             'issuing_officer']
        ).values_list('id', flat=True)
        return EmailUser.objects.filter(
            groups__id__in=groups
        ).distinct()

    @property
    def licence_type_short_name(self):
        return self.licence_category

    @property
    def licence_type_data(self):
        from wildlifecompliance.components.licences.serializers import LicenceCategorySerializer

        serializer = LicenceCategorySerializer(
            self.licence_purposes.first().licence_category,
            context={
                'purpose_records': self.licence_purposes
            }
        )
        licence_data = serializer.data
        for activity in licence_data['activity']:
            selected_activity = self.get_selected_activity(activity['id'])
            activity['processing_status'] = {
                'id': selected_activity.processing_status,
                'name': get_choice_value(
                    selected_activity.processing_status,
                    ApplicationSelectedActivity.PROCESSING_STATUS_CHOICES
                )
            }
            activity['start_date'] = selected_activity.start_date
            activity['expiry_date'] = selected_activity.expiry_date
        return licence_data

    @property
    def licence_category_name(self):
        first_activity = self.licence_purposes.first()
        try:
            activity_category = first_activity.licence_category.short_name
        except AttributeError:
            activity_category = ''
        return activity_category

    @property
    def licence_activity_names(self):
        return list(self.licence_purposes.all().values_list(
            'licence_activity__short_name', flat=True
        ).distinct())

    @property
    def licence_purpose_names(self):
        return ', '.join([purpose.short_name
                          for purpose in self.licence_purposes.all().order_by('licence_activity','short_name')])

    @property
    def licence_type_name(self):
        from wildlifecompliance.components.licences.models import LicenceActivity
        licence_category = self.licence_category_name
        licence_activity_purposes = []
        activity_id_list = self.licence_purposes.all().order_by('licence_activity_id').values_list('licence_activity_id', flat=True).distinct()
        for activity_id in activity_id_list:
            try:
                activity_short_name = LicenceActivity.objects.get(id=activity_id).short_name
            except AttributeError:
                activity_short_name = ''
            purpose_list = ', '.join(self.licence_purposes.filter(licence_activity_id=activity_id).values_list('short_name', flat=True))
            licence_activity_purposes.append('{} ({})'.format(activity_short_name, purpose_list))
        licence_activity_purposes_string = ', '.join(licence_activity_purposes)
        return ' {licence_category}{activities_purposes}'.format(
            licence_category="{} - ".format(licence_category) if licence_category else "",
            activities_purposes="{}".format(licence_activity_purposes_string) if licence_activity_purposes_string else ''
        )

    @property
    def licence_category_id(self):
        try:
            return self.licence_purposes.first().licence_category.id
        except AttributeError:
            return ''

    @property
    def licence_category(self):
        try:
            return self.licence_purposes.first().licence_category.display_name
        except AttributeError:
            return ''

    def set_activity_processing_status(self, activity_id, processing_status):
        if not activity_id:
            logger.error("Application: %s cannot update processing status (%s) for an empty activity_id!" %
                         (self.id, processing_status))
            return
        if processing_status not in dict(ApplicationSelectedActivity.PROCESSING_STATUS_CHOICES):
            logger.error("Application: %s cannot update processing status (%s) for invalid processing status!" %
                         (self.id, processing_status))
            return
        selected_activity = self.get_selected_activity(activity_id)
        selected_activity.processing_status = processing_status
        selected_activity.save()
        logger.info("Application: %s Activity ID: %s changed processing to: %s" % (self.id, activity_id, processing_status))

    def get_selected_activity(self, activity_id):
        if activity_id is None:
            return ApplicationSelectedActivity.objects.none()

        selected_activity = ApplicationSelectedActivity.objects.filter(
            application_id=self.id,
            licence_activity_id=activity_id
        ).first()
        if not selected_activity:
            selected_activity = ApplicationSelectedActivity.objects.create(
                application_id=self.id,
                licence_activity_id=activity_id
            )
        return selected_activity

    def get_licence_category(self):
        first_activity = self.licence_purposes.first()
        try:
            return first_activity.licence_category
        except AttributeError:
            return LicenceCategory.objects.none()

    def get_permission_groups(self, codename):
        """
        :return: queryset of ActivityPermissionGroups matching the current application by activity IDs
        """
        selected_activity_ids = ApplicationSelectedActivity.objects.filter(
            application_id=self.id,
            licence_activity__isnull=False
        ).values_list('licence_activity__id', flat=True)
        if not selected_activity_ids:
            return ActivityPermissionGroup.objects.none()

        return ActivityPermissionGroup.get_groups_for_activities(selected_activity_ids, codename)

    def log_user_action(self, action, request):
        return ApplicationUserAction.log_action(self, action, request.user)

    def calculate_fees(self, data_source):
        return self.get_dynamic_schema_attributes(data_source)['fees']

    def get_dynamic_schema_attributes(self, data_source):
        dynamic_attributes = {
            'fees': Application.calculate_base_fees(
                self.licence_purposes.values_list('id', flat=True)
            ),
            'activity_attributes': {},
        }

        def parse_modifiers(dynamic_attributes, component, schema_name, adjusted_by_fields, activity):
            def increase_fee(fees, field, amount):
                fees[field] += amount
                fees[field] = fees[field] if fees[field] >= 0 else 0
                return True

            fee_modifier_keys = {
                'IncreaseLicenceFee': 'licence',
                'IncreaseApplicationFee': 'application',
            }
            increase_limit_key = 'IncreaseTimesLimit'
            try:
                increase_count = adjusted_by_fields[schema_name]
            except KeyError:
                increase_count = adjusted_by_fields[schema_name] = 0

            # Does this component / selected option enable the inspection requirement?
            try:
                # If at least one component has a positive value - require inspection for the entire activity.
                if component['InspectionRequired']:
                    dynamic_attributes['activity_attributes'][activity]['is_inspection_required'] = True
            except KeyError:
                pass

            if increase_limit_key in component:
                max_increases = int(component[increase_limit_key])
                if increase_count >= max_increases:
                    return

            adjustments_performed = sum(key in component and increase_fee(
                dynamic_attributes['fees'],
                field,
                component[key]
            ) and increase_fee(
                dynamic_attributes['activity_attributes'][activity]['fees'],
                field,
                component[key]
            ) for key, field in fee_modifier_keys.items())

            if adjustments_performed:
                adjusted_by_fields[schema_name] += 1

        for selected_activity in self.activities:
            schema_fields = self.get_schema_fields_for_purposes(
                selected_activity.purposes.values_list('id', flat=True)
            )
            dynamic_attributes['activity_attributes'][selected_activity] = {
                'is_inspection_required': False,
                'fees': selected_activity.base_fees,
            }

            # Adjust fees based on selected options (radios and checkboxes)
            adjusted_by_fields = {}
            for form_data_record in data_source:
                try:
                    # Retrieve dictionary of fields from a model instance
                    data_record = form_data_record.__dict__
                except AttributeError:
                    # If a raw form data (POST) is supplied, form_data_record is a key
                    data_record = data_source[form_data_record]

                schema_name = data_record['schema_name']
                if schema_name not in schema_fields:
                    continue
                schema_data = schema_fields[schema_name]

                if 'options' in schema_data:
                    for option in schema_data['options']:
                        # Only consider fee modifications if the current option is selected
                        if option['value'] != data_record['value']:
                            continue
                        parse_modifiers(
                            dynamic_attributes=dynamic_attributes,
                            component=option,
                            schema_name=schema_name,
                            adjusted_by_fields=adjusted_by_fields,
                            activity=selected_activity
                        )

                # If this is a checkbox - skip unchecked ones
                elif data_record['value'] == 'on':
                    parse_modifiers(
                        dynamic_attributes=dynamic_attributes,
                        component=schema_data,
                        schema_name=schema_name,
                        adjusted_by_fields=adjusted_by_fields,
                        activity=selected_activity
                    )

        return dynamic_attributes

    def update_dynamic_attributes(self):
        """ Update application and activity attributes based on selected JSON schema options. """
        if self.processing_status != Application.PROCESSING_STATUS_DRAFT:
            return

        dynamic_attributes = self.get_dynamic_schema_attributes(self.data)

        # Update application and licence fees
        fees = dynamic_attributes['fees']

        # Amendments are always free.
        if self.application_type in [
            Application.APPLICATION_TYPE_AMENDMENT,
        ]:
            self.application_fee = Decimal(0)
        else:
            self.application_fee = fees['application']
        self.save()

        # Save any parsed per-activity modifiers
        for selected_activity, field_data in dynamic_attributes['activity_attributes'].items():
            fees = field_data.pop('fees', {})
            if self.application_type == Application.APPLICATION_TYPE_AMENDMENT:
                selected_activity.licence_fee = Decimal(0)
            else:
                selected_activity.licence_fee = fees['licence']
            for field, value in field_data.items():
                setattr(selected_activity, field, value)
                selected_activity.save()

    def submit(self, request):
        from wildlifecompliance.components.licences.models import LicenceActivity
        with transaction.atomic():
            if self.can_user_edit:
                if not self.application_fee_paid:
                    self.customer_status = Application.CUSTOMER_STATUS_AWAITING_PAYMENT
                    self.save()
                    return
                self.customer_status = Application.CUSTOMER_STATUS_UNDER_REVIEW
                self.submitter = request.user
                self.lodgement_date = timezone.now()
                # if amendment is submitted change the status of only particular activity
                # else if the new application is submitted change the status of
                # all the activities
                if (self.amendment_requests):
                    qs = self.amendment_requests.filter(status=AmendmentRequest.AMENDMENT_REQUEST_STATUS_REQUESTED)
                    if (qs):
                        for q in qs:
                            q.status = AmendmentRequest.AMENDMENT_REQUEST_STATUS_AMENDED
                            self.set_activity_processing_status(
                                q.licence_activity.id, ApplicationSelectedActivity.PROCESSING_STATUS_WITH_OFFICER)
                            q.save()
                else:
                    for activity in self.licence_type_data['activity']:
                        if activity["processing_status"]["id"] != ApplicationSelectedActivity.PROCESSING_STATUS_DRAFT:
                            continue
                        self.set_activity_processing_status(
                            activity["id"], ApplicationSelectedActivity.PROCESSING_STATUS_WITH_OFFICER)
                        qs = DefaultCondition.objects.filter(
                            licence_activity=activity["id"])
                        if (qs):
                            for q in qs:
                                ApplicationCondition.objects.create(
                                    default_condition=q,
                                    is_default=True,
                                    standard=False,
                                    application=self,
                                    licence_activity=LicenceActivity.objects.get(
                                        id=activity["id"]),
                                    return_type=q.return_type)

                self.save()
                officer_groups = ActivityPermissionGroup.objects.filter(
                    permissions__codename='licensing_officer',
                    licence_activities__purpose__licence_category__id=self.licence_type_data["id"]
                )
                group_users = EmailUser.objects.filter(
                    groups__id__in=officer_groups.values_list('id', flat=True)
                ).distinct()

                if self.amendment_requests:
                    self.log_user_action(
                        ApplicationUserAction.ACTION_ID_REQUEST_AMENDMENTS_SUBMIT.format(
                            self.id), request)
                    send_amendment_submit_email_notification(
                        group_users, self, request)
                else:
                    # Create a log entry for the application
                    self.log_user_action(
                        ApplicationUserAction.ACTION_LODGE_APPLICATION.format(
                            self.id), request)
                    # Create a log entry for the applicant (submitter,
                    # organisation or proxy)
                    if self.org_applicant:
                        self.org_applicant.log_user_action(
                            ApplicationUserAction.ACTION_LODGE_APPLICATION.format(
                                self.id), request)
                    elif self.proxy_applicant:
                        self.proxy_applicant.log_user_action(
                            ApplicationUserAction.ACTION_LODGE_APPLICATION.format(
                                self.id), request)
                    else:
                        self.submitter.log_user_action(
                            ApplicationUserAction.ACTION_LODGE_APPLICATION.format(
                                self.id), request)
                    # Send email to submitter, then to linked Officer Groups
                    send_application_submitter_email_notification(
                        self, request)

                    send_application_submit_email_notification(
                        group_users, self, request)

                    self.documents.all().update(can_delete=False)

            else:
                raise ValidationError(
                    'You can\'t edit this application at this moment')

    def accept_id_check(self, request):
        self.id_check_status = Application.ID_CHECK_STATUS_ACCEPTED
        self.save()
        # Create a log entry for the application
        self.log_user_action(
            ApplicationUserAction.ACTION_ACCEPT_ID.format(
                self.id), request)
        # Create a log entry for the applicant (submitter, organisation or
        # proxy)
        if self.org_applicant:
            self.org_applicant.log_user_action(
                ApplicationUserAction.ACTION_ACCEPT_ID.format(
                    self.id), request)
        elif self.proxy_applicant:
            self.proxy_applicant.log_user_action(
                ApplicationUserAction.ACTION_ACCEPT_ID.format(
                    self.id), request)
        else:
            self.submitter.log_user_action(
                ApplicationUserAction.ACTION_ACCEPT_ID.format(
                    self.id), request)

    def reset_id_check(self, request):
        self.id_check_status = Application.ID_CHECK_STATUS_NOT_CHECKED
        self.save()
        # Create a log entry for the application
        self.log_user_action(
            ApplicationUserAction.ACTION_RESET_ID.format(
                self.id), request)
        # Create a log entry for the applicant (submitter, organisation or
        # proxy)
        if self.org_applicant:
            self.org_applicant.log_user_action(
                ApplicationUserAction.ACTION_RESET_ID.format(
                    self.id), request)
        elif self.proxy_applicant:
            self.proxy_applicant.log_user_action(
                ApplicationUserAction.ACTION_RESET_ID.format(
                    self.id), request)
        else:
            self.submitter.log_user_action(
                ApplicationUserAction.ACTION_RESET_ID.format(
                    self.id), request)

    def request_id_check(self, request):
        self.id_check_status = Application.ID_CHECK_STATUS_AWAITING_UPDATE
        self.save()
        # Create a log entry for the application
        self.log_user_action(
            ApplicationUserAction.ACTION_ID_REQUEST_UPDATE.format(
                self.id), request)
        # Create a log entry for the applicant (submitter or organisation only)
        if self.org_applicant:
            self.org_applicant.log_user_action(
                ApplicationUserAction.ACTION_ID_REQUEST_UPDATE.format(
                    self.id), request)
        elif self.proxy_applicant:
            # do nothing if proxy_applicant
            pass
        else:
            self.submitter.log_user_action(
                ApplicationUserAction.ACTION_ID_REQUEST_UPDATE.format(
                    self.id), request)
        # send email to submitter or org_applicant admins
        if self.org_applicant:
            send_org_id_update_request_notification(self, request)
        elif self.proxy_applicant:
            # do nothing if proxy_applicant
            pass
        else:
            # send to submitter
            send_id_update_request_notification(self, request)

    def accept_character_check(self, request):
        self.character_check_status = Application.CHARACTER_CHECK_STATUS_ACCEPTED
        self.save()
        # Create a log entry for the application
        self.log_user_action(
            ApplicationUserAction.ACTION_ACCEPT_CHARACTER.format(
                self.id), request)
        # Create a log entry for the applicant (submitter, organisation or
        # proxy)
        if self.org_applicant:
            self.org_applicant.log_user_action(
                ApplicationUserAction.ACTION_ACCEPT_CHARACTER.format(
                    self.id), request)
        elif self.proxy_applicant:
            self.proxy_applicant.log_user_action(
                ApplicationUserAction.ACTION_ACCEPT_CHARACTER.format(
                    self.id), request)
        else:
            self.submitter.log_user_action(
                ApplicationUserAction.ACTION_ACCEPT_CHARACTER.format(
                    self.id), request)

    def assign_officer(self, request, officer):
        with transaction.atomic():
            try:
                if officer != self.assigned_officer:
                    self.assigned_officer = officer
                    self.save()
                    # Create a log entry for the application
                    self.log_user_action(ApplicationUserAction.ACTION_ASSIGN_TO_OFFICER.format(
                        self.id, '{}({})'.format(officer.get_full_name(), officer.email)), request)
            except BaseException:
                raise

    def unassign_officer(self, request):
        with transaction.atomic():
            try:
                if self.assigned_officer:
                    self.assigned_officer = None
                    self.save()
                    # Create a log entry for the application
                    self.log_user_action(
                        ApplicationUserAction.ACTION_UNASSIGN_OFFICER.format(
                            self.id), request)
            except BaseException:
                raise

    def return_to_officer_conditions(self, request, activity_id):
        text = request.data.get('text', '')
        if self.assigned_officer:
            email_list = [self.assigned_officer.email]
        else:
            officer_groups = ActivityPermissionGroup.objects.filter(
                permissions__codename='licensing_officer',
                licence_activities__id=activity_id
            )
            group_users = EmailUser.objects.filter(
                groups__id__in=officer_groups.values_list('id', flat=True)
            ).distinct()
            email_list = [user.email for user in group_users]

        self.set_activity_processing_status(
            activity_id,
            ApplicationSelectedActivity.PROCESSING_STATUS_OFFICER_CONDITIONS
        )
        send_application_return_to_officer_conditions_notification(
            email_list=email_list,
            application=self,
            text=text,
            request=request
        )

    def complete_assessment(self, request):
        with transaction.atomic():
            try:
                assessment_id = request.data.get('assessment_id')
                activity_id = int(request.data.get('selected_assessment_tab', 0))

                assessment = Assessment.objects.filter(
                    id=assessment_id,
                    licence_activity_id=activity_id,
                    status=Assessment.STATUS_AWAITING_ASSESSMENT,
                    application=self
                ).first()

                if not assessment:
                    raise Exception("Assessment record ID %s (activity: %s) does not exist!" % (
                        assessment_id, activity_id))

                assessor_group = request.user.get_wildlifelicence_permission_group(
                    permission_codename='assessor',
                    activity_id=assessment.licence_activity_id,
                    first=True
                )
                if not assessor_group:
                    raise Exception("Missing assessor permissions for Activity ID: %s" % (
                        assessment.licence_activity_id))

                assessment.status = Assessment.STATUS_COMPLETED
                assessment.actioned_by = request.user
                assessment.save()
                # Log application action
                self.log_user_action(
                    ApplicationUserAction.ACTION_ASSESSMENT_COMPLETE.format(assessor_group), request)
                # Log entry for organisation
                if self.org_applicant:
                    self.org_applicant.log_user_action(
                        ApplicationUserAction.ACTION_ASSESSMENT_COMPLETE.format(assessor_group), request)
                elif self.proxy_applicant:
                    self.proxy_applicant.log_user_action(
                        ApplicationUserAction.ACTION_ASSESSMENT_COMPLETE.format(assessor_group), request)
                else:
                    self.submitter.log_user_action(
                        ApplicationUserAction.ACTION_ASSESSMENT_COMPLETE.format(assessor_group), request)

                self.check_assessment_complete(activity_id)
            except BaseException:
                raise

    def check_assessment_complete(self, activity_id):
        # check if this is the last assessment for current
        # application, Change the processing status only if it is the
        # last assessment
        if not Assessment.objects.filter(
                application=self,
                licence_activity=activity_id,
                status=Assessment.STATUS_AWAITING_ASSESSMENT).exists():
            for activity in self.licence_type_data['activity']:
                if activity_id == activity["id"]:
                    self.set_activity_processing_status(
                        activity["id"], ApplicationSelectedActivity.PROCESSING_STATUS_OFFICER_CONDITIONS)

    def proposed_decline(self, request, details):
        with transaction.atomic():
            try:
                activity_list = details.get('activity')
                incorrect_statuses = ApplicationSelectedActivity.objects.filter(
                    application_id=self.id,
                    licence_activity_id__in=activity_list
                ).exclude(
                    processing_status=ApplicationSelectedActivity.PROCESSING_STATUS_OFFICER_CONDITIONS
                ).first()

                if incorrect_statuses:
                    raise ValidationError(
                        'You cannot propose for licence if it is not with officer for conditions')

                ApplicationSelectedActivity.objects.filter(
                    application_id=self.id,
                    licence_activity_id__in=activity_list
                ).update(
                    updated_by=request.user,
                    proposed_action=ApplicationSelectedActivity.PROPOSED_ACTION_DECLINE,
                    processing_status=ApplicationSelectedActivity.PROCESSING_STATUS_OFFICER_FINALISATION,
                    reason=details.get('reason'),
                    cc_email=details.get('cc_email', None),
                )

                # Log application action
                self.log_user_action(
                    ApplicationUserAction.ACTION_PROPOSED_DECLINE.format(
                        self.id), request)
                # Log entry for organisation
                if self.org_applicant:
                    self.org_applicant.log_user_action(
                        ApplicationUserAction.ACTION_PROPOSED_DECLINE.format(
                            self.id), request)
                elif self.proxy_applicant:
                    self.proxy_applicant.log_user_action(
                        ApplicationUserAction.ACTION_PROPOSED_DECLINE.format(
                            self.id), request)
                else:
                    self.submitter.log_user_action(
                        ApplicationUserAction.ACTION_PROPOSED_DECLINE.format(
                            self.id), request)
            except BaseException:
                raise

    def send_to_assessor(self, request):
        with transaction.atomic():
            try:
                Assessment.objects.update_or_create(
                    application=self,
                    officer=request.user,
                    reason=request.data.get('reason'),
                )

                # Log application action
                self.log_user_action(
                    ApplicationUserAction.ACTION_SEND_FOR_ASSESSMENT_TO_.format(
                        self.id), request)
            except BaseException:
                raise

    @property
    def amendment_requests(self):
        return AmendmentRequest.objects.filter(application=self)

    @property
    def active_amendment_requests(self):
        activity_ids = self.activities.values_list('licence_activity_id', flat=True)
        return self.amendment_requests.filter(licence_activity_id__in=activity_ids)

    @property
    def assessments(self):
        qs = Assessment.objects.filter(
            application=self, status=Assessment.STATUS_AWAITING_ASSESSMENT)
        return qs

    @property
    def licences(self):
        from wildlifecompliance.components.licences.models import WildlifeLicence
        try:
            return WildlifeLicence.objects.filter(current_application=self)
        except WildlifeLicence.DoesNotExist:
            return WildlifeLicence.objects.none()

    @property
    def required_fields(self):
        return {key: data for key, data in self.schema_fields.items() if 'isRequired' in data and data['isRequired']}

    @property
    def schema_fields(self):
        return self.get_schema_fields(self.schema)

    @property
    def schema(self):
        return self.get_schema_for_purposes(
            self.licence_purposes.values_list('id', flat=True)
        )

    @property
    def data(self):
        """ returns a queryset of form data records attached to application (shortcut to ApplicationFormDataRecord related_name). """
        return self.form_data_records.all()

    @property
    def activities(self):
        """ returns a queryset of activities attached to application (shortcut to ApplicationSelectedActivity related_name). """
        return self.selected_activities.exclude(processing_status=ApplicationSelectedActivity.PROCESSING_STATUS_DISCARDED)

    def get_activity_chain(self, **activity_filters):
        activity_chain = self.selected_activities.filter(**activity_filters)
        return activity_chain | self.previous_application.get_activity_chain(
            **activity_filters
        ) if self.previous_application and self.previous_application != self else activity_chain

    def get_latest_current_activity(self, activity_id):
        return self.get_activity_chain(
            licence_activity_id=activity_id,
            activity_status=ApplicationSelectedActivity.ACTIVITY_STATUS_CURRENT
        ).order_by(
            '-issue_date'
        ).first()

    def get_schema_fields_for_purposes(self, purpose_id_list):
        return self.get_schema_fields(
            self.get_schema_for_purposes(purpose_id_list)
        )

    def get_schema_for_purposes(self, purpose_id_list):
        from wildlifecompliance.components.applications.utils import get_activity_schema
        return get_activity_schema(purpose_id_list)

    def get_schema_fields(self, schema_json):
        fields = {}

        print('\n\nschema_json')
        print(schema_json)
        print('schema_json\n\n')
        def iterate_children(schema_group, fields, parent={}, parent_type='', condition={}, activity_id=None):
            children_keys = [
                'children',
                'header',
                'expander',
                'conditions',
            ]
            container = {
                i: schema_group[i] for i in range(len(schema_group))
            } if isinstance(schema_group, list) else schema_group

            for key, item in container.items():
                if isinstance(item, list):
                    if parent_type == 'conditions':
                        condition[parent['name']] = key
                    iterate_children(item, fields, parent, parent_type, condition, activity_id)
                    continue

                try:
                    activity_id = item['id']
                except BaseException:
                    pass

                name = item['name']
                fields[name] = {}
                fields[name].update(item)
                fields[name]['condition'] = {}
                fields[name]['condition'].update(condition)
                fields[name]['activity_id'] = activity_id

                for children_key in children_keys:
                    if children_key in fields[name]:
                        del fields[name][children_key]
                        iterate_children(item[children_key], fields, fields[name], children_key, condition, activity_id)
                condition = {}

        iterate_children(schema_json, fields)
        print('\n\nfields')
        print(fields)
        print('fields\n\n')
        return fields

    def get_visible_form_data_tree(self, form_data_records=None):
        data_tree = {}
        schema_fields = self.schema_fields

        if form_data_records is None:
            form_data_records = [(record.field_name, {
                'schema_name': record.schema_name,
                'instance_name': record.instance_name,
                'value': record.value,
            }) for record in self.form_data_records.all()]

        for field_name, item in form_data_records:
            instance = item['instance_name']
            schema_name = item['schema_name']

            if instance not in data_tree:
                data_tree[instance] = {}
            data_tree[instance][schema_name] = item['value']

        for instance, schemas in data_tree.items():
            for schema_name, item in schemas.items():
                if schema_name not in schema_fields:
                    continue
                schema_data = schema_fields[schema_name]
                for condition_field, condition_value in schema_data['condition'].items():
                    if condition_field in schemas and schemas[condition_field] != condition_value:
                        try:
                            del data_tree[instance][schema_name]
                        except KeyError:
                            continue

        return data_tree

    def get_licences_by_status(self, status):
        return self.licences.filter(current_application__selected_activities__activity_status=status).distinct()

    def get_proposed_decisions(self, request):
        with transaction.atomic():
            try:
                proposed_states = [ApplicationSelectedActivity.PROPOSED_ACTION_DECLINE,
                                   ApplicationSelectedActivity.PROPOSED_ACTION_ISSUE
                                   ]
                qs = ApplicationSelectedActivity.objects.filter(
                    application=self, proposed_action__in=proposed_states)
                for q in qs:
                    if ApplicationSelectedActivity.objects.filter(
                            application=self,
                            licence_activity=q.licence_activity,
                            decision_action__isnull=False).exists():
                        qs.exclude(id=q.id)
                return qs
            except BaseException:
                raise

    def proposed_licence(self, request, details):
        with transaction.atomic():
            try:
                activity_list = details.get('activity', [])
                incorrect_statuses = ApplicationSelectedActivity.objects.filter(
                    application_id=self.id,
                    licence_activity_id__in=activity_list
                ).exclude(
                    processing_status=ApplicationSelectedActivity.PROCESSING_STATUS_OFFICER_CONDITIONS
                ).first()

                if incorrect_statuses:
                    raise ValidationError(
                        'You cannot propose for licence if it is not with officer for conditions')

                if self.application_type == Application.APPLICATION_TYPE_AMENDMENT:
                    # Pre-populate proposed issue dates with dates from the currently active licence.
                    for activity_id in activity_list:
                        latest_activity = self.get_latest_current_activity(activity_id)
                        if not latest_activity:
                            raise Exception("Active licence not found for activity ID: %s" % activity_id)

                        activity = self.activities.get(
                            licence_activity_id=activity_id
                        )
                        activity.updated_by = request.user
                        activity.proposed_action = ApplicationSelectedActivity.PROPOSED_ACTION_ISSUE
                        activity.processing_status = ApplicationSelectedActivity.PROCESSING_STATUS_OFFICER_FINALISATION
                        activity.reason = details.get('reason')
                        activity.cc_email = details.get('cc_email', None)
                        activity.proposed_start_date = latest_activity.start_date
                        activity.proposed_end_date = latest_activity.expiry_date
                        activity.save()

                        # Update the current (now old) activity
                        latest_activity.updated_by = request.user
                        latest_activity.activity_status = ApplicationSelectedActivity.ACTIVITY_STATUS_REPLACED
                        latest_activity.save()
                else:
                    ApplicationSelectedActivity.objects.filter(
                        application_id=self.id,
                        licence_activity_id__in=activity_list
                    ).update(
                        updated_by=request.user,
                        proposed_action=ApplicationSelectedActivity.PROPOSED_ACTION_ISSUE,
                        processing_status=ApplicationSelectedActivity.PROCESSING_STATUS_OFFICER_FINALISATION,
                        reason=details.get('reason'),
                        cc_email=details.get('cc_email', None),
                        proposed_start_date=details.get('start_date', None),
                        proposed_end_date=details.get('expiry_date', None),
                    )

                # Log application action
                self.log_user_action(
                    ApplicationUserAction.ACTION_PROPOSED_LICENCE.format(
                        self.id), request)
                # Log entry for organisation
                if self.org_applicant:
                    self.org_applicant.log_user_action(
                        ApplicationUserAction.ACTION_PROPOSED_LICENCE.format(
                            self.id), request)
                elif self.proxy_applicant:
                    self.proxy_applicant.log_user_action(
                        ApplicationUserAction.ACTION_PROPOSED_LICENCE.format(
                            self.id), request)
                else:
                    self.submitter.log_user_action(
                        ApplicationUserAction.ACTION_PROPOSED_LICENCE.format(
                            self.id), request)
            except BaseException:
                raise

    def get_parent_licence(self):
        from wildlifecompliance.components.licences.models import WildlifeLicence
        current_date = timezone.now().date()
        try:
            existing_licence = WildlifeLicence.objects.filter(
                Q(licence_category=self.get_licence_category()),
                Q(current_application__org_applicant_id=self.org_applicant_id) if self.org_applicant_id else (
                    Q(current_application__submitter_id=self.proxy_applicant_id
                      ) | Q(current_application__proxy_applicant_id=self.proxy_applicant_id)
                ) if self.proxy_applicant_id else Q(current_application__submitter_id=self.submitter_id)
            ).order_by('-id').distinct().first()

            if existing_licence:
                # Only load licence if any associated activities are still current.
                if not existing_licence.current_application.get_activity_chain(
                    expiry_date__gte=current_date,
                    activity_status=ApplicationSelectedActivity.ACTIVITY_STATUS_CURRENT
                ).first():
                    raise WildlifeLicence.DoesNotExist
            else:
                raise WildlifeLicence.DoesNotExist
            return existing_licence, False
        except WildlifeLicence.DoesNotExist:
            return WildlifeLicence.objects.create(
                current_application=self,
                licence_category=self.get_licence_category()
            ), True

    def final_decision(self, request):
        failed_payment_activities = []

        with transaction.atomic():
            try:
                parent_licence, created = self.get_parent_licence()
                issued_activities = []
                declined_activities = []
                for item in request.data.get('activity'):
                    licence_activity_id = item['id']
                    selected_activity = self.activities.filter(
                        licence_activity__id=licence_activity_id
                    ).first()
                    if not selected_activity:
                        raise Exception("Licence activity %s is missing from Application ID %s!" % (
                            licence_activity_id, self.id))

                    if selected_activity.processing_status not in [
                        ApplicationSelectedActivity.PROCESSING_STATUS_OFFICER_FINALISATION,
                        ApplicationSelectedActivity.PROCESSING_STATUS_AWAITING_LICENCE_FEE_PAYMENT,
                    ]:
                        raise Exception("Activity \"%s\" has an invalid processing status: %s" % (
                            selected_activity.licence_activity.name, selected_activity.processing_status))

                    if item['final_status'] == ApplicationSelectedActivity.DECISION_ACTION_ISSUED:

                        # If there is an outstanding licence fee payment - attempt to charge the stored card.
                        if not selected_activity.process_licence_fee_payment(request, self):
                            failed_payment_activities.append(selected_activity)
                            continue

                        original_issue_date = start_date = item.get('start_date')
                        expiry_date = item.get('end_date')

                        if self.application_type == Application.APPLICATION_TYPE_AMENDMENT:
                            latest_activity = self.get_latest_current_activity(licence_activity_id)
                            if not latest_activity:
                                raise Exception("Active licence not found for activity ID: %s" % licence_activity_id)

                            # Populate start and expiry dates from the latest issued activity record
                            original_issue_date = latest_activity.original_issue_date
                            start_date = latest_activity.start_date
                            expiry_date = latest_activity.expiry_date

                            # Set activity_status for latest_activity to REPLACED
                            latest_activity.activity_status = ApplicationSelectedActivity.ACTIVITY_STATUS_REPLACED
                            latest_activity.save()

                        selected_activity.issue_date = timezone.now()
                        selected_activity.updated_by = request.user
                        selected_activity.decision_action = ApplicationSelectedActivity.DECISION_ACTION_ISSUED
                        selected_activity.processing_status = ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED
                        selected_activity.original_issue_date = original_issue_date
                        selected_activity.start_date = start_date
                        selected_activity.expiry_date = expiry_date
                        selected_activity.cc_email = item['cc_email']
                        selected_activity.reason = item['reason']
                        selected_activity.activity_status = ApplicationSelectedActivity.ACTIVITY_STATUS_CURRENT
                        selected_activity.save()
                        issued_activities.append(selected_activity)

                        self.generate_returns(parent_licence, selected_activity, request)
                        # Log application action
                        self.log_user_action(
                            ApplicationUserAction.ACTION_ISSUE_LICENCE_.format(
                                item['name']), request)
                        # Log entry for organisation
                        if self.org_applicant:
                            self.org_applicant.log_user_action(
                                ApplicationUserAction.ACTION_ISSUE_LICENCE_.format(
                                    item['name']), request)
                        elif self.proxy_applicant:
                            self.proxy_applicant.log_user_action(
                                ApplicationUserAction.ACTION_ISSUE_LICENCE_.format(
                                    item['name']), request)
                        else:
                            self.submitter.log_user_action(
                                ApplicationUserAction.ACTION_ISSUE_LICENCE_.format(
                                    item['name']), request)
                    elif item['final_status'] == ApplicationSelectedActivity.DECISION_ACTION_DECLINED:
                        selected_activity.updated_by = request.user
                        selected_activity.processing_status = ApplicationSelectedActivity.PROCESSING_STATUS_DECLINED
                        selected_activity.decision_action = ApplicationSelectedActivity.DECISION_ACTION_ISSUED
                        selected_activity.cc_email = item['cc_email']
                        selected_activity.reason = item['reason']
                        selected_activity.save()
                        declined_activities.append(selected_activity)
                        # Log application action
                        self.log_user_action(
                            ApplicationUserAction.ACTION_DECLINE_LICENCE_.format(
                                item['name']), request)
                        # Log entry for organisation
                        if self.org_applicant:
                            self.org_applicant.log_user_action(
                                ApplicationUserAction.ACTION_DECLINE_LICENCE_.format(
                                    item['name']), request)
                        elif self.proxy_applicant:
                            self.proxy_applicant.log_user_action(
                                ApplicationUserAction.ACTION_DECLINE_LICENCE_.format(
                                    item['name']), request)
                        else:
                            self.submitter.log_user_action(
                                ApplicationUserAction.ACTION_DECLINE_LICENCE_.format(
                                    item['name']), request)

                if issued_activities:
                    # Re-generate PDF document using all finalised activities
                    parent_licence.current_application = self
                    if not created:
                        parent_licence.licence_sequence += 1
                    parent_licence.generate_doc()
                    send_application_issue_notification(
                        activities=issued_activities,
                        application=self,
                        request=request,
                        licence=parent_licence
                    )

                if declined_activities:
                    send_application_decline_notification(
                        declined_activities, self, request)

            except BaseException:
                raise

        if failed_payment_activities:
            for activity in failed_payment_activities:
                activity.processing_status = ApplicationSelectedActivity.PROCESSING_STATUS_AWAITING_LICENCE_FEE_PAYMENT
                activity.save()
            raise Exception("Could not process licence fee payment for: {}".format(
                ", ".join([activity.licence_activity.name for activity in failed_payment_activities])
            ))

    def generate_returns(self, licence, selected_activity, request):
        from wildlifecompliance.components.returns.models import Return
        licence_expiry = selected_activity.expiry_date
        licence_expiry = datetime.datetime.strptime(
            licence_expiry, "%Y-%m-%d"
        ).date() if isinstance(licence_expiry, six.string_types) else licence_expiry
        today = timezone.now().date()
        timedelta = datetime.timedelta
        for condition in self.conditions.all():
            try:
                if condition.due_date and condition.due_date >= today:
                    current_date = condition.due_date
                    # create a first Return
                    try:
                        Return.objects.get(
                            condition=condition, due_date=current_date)
                    except Return.DoesNotExist:
                        Return.objects.create(
                            application=self,
                            due_date=current_date,
                            processing_status=Return.RETURN_PROCESSING_STATUS_FUTURE,
                            licence=licence,
                            condition=condition,
                            return_type=condition.return_type,
                            submitter=request.user
                        )
                        # compliance.log_user_action(ComplianceUserAction.ACTION_CREATE.format(compliance.id),request)
                    if condition.recurrence:
                        while current_date < licence_expiry:
                            for x in range(condition.recurrence_schedule):
                                # Weekly
                                if condition.recurrence_pattern == ApplicationCondition\
                                        .APPLICATION_CONDITION_RECURRENCE_WEEKLY:
                                            current_date += timedelta(weeks=1)
                            # Monthly
                                elif condition.recurrence_pattern == ApplicationCondition\
                                        .APPLICATION_CONDITION_RECURRENCE_MONTHLY:
                                            current_date += timedelta(weeks=4)
                                            pass
                            # Yearly
                                elif condition.recurrence_pattern == ApplicationCondition\
                                        .APPLICATION_CONDITION_RECURRENCE_YEARLY:
                                            current_date += timedelta(days=365)
                            # Create the Return
                            if current_date <= licence_expiry:
                                try:
                                    Return.objects.get(
                                        condition=condition, due_date=current_date)
                                except Return.DoesNotExist:
                                    Return.objects.create(
                                        application=self,
                                        due_date=current_date,
                                        processing_status=Return.RETURN_PROCESSING_STATUS_FUTURE,
                                        licence=licence,
                                        condition=condition,
                                        return_type=condition.return_type
                                    )
            except BaseException:
                raise

    @staticmethod
    def calculate_base_fees(selected_purpose_ids):
        from wildlifecompliance.components.licences.models import LicencePurpose

        base_fees = {
            'application': Decimal(0.0),
            'licence': Decimal(0.0),
        }

        for purpose in LicencePurpose.objects.filter(id__in=selected_purpose_ids):
            base_fees['application'] += purpose.base_application_fee
            base_fees['licence'] += purpose.base_licence_fee

        return base_fees

    @staticmethod
    def get_activity_date_filter(for_application_type, prefix=''):
        current_date = timezone.now().date()
        date_filter = {
            '{}expiry_date__isnull'.format(prefix): False,
            '{}expiry_date__gte'.format(prefix): current_date
        }
        if for_application_type == Application.APPLICATION_TYPE_RENEWAL:
            expires_at = current_date + datetime.timedelta(days=settings.RENEWAL_PERIOD_DAYS)
            date_filter = {
                '{}expiry_date__isnull'.format(prefix): False,
                '{}expiry_date__gte'.format(prefix): current_date,
                '{}expiry_date__lte'.format(prefix): expires_at,
            }
        return date_filter

    @staticmethod
    def get_active_licence_activities(request, for_application_type=APPLICATION_TYPE_NEW_LICENCE):
        applications = Application.get_active_licence_applications(request, for_application_type)
        return ApplicationSelectedActivity.get_current_activities_for_application_type(
            for_application_type,
            applications=applications
        )

    @staticmethod
    def get_active_licence_applications(request, for_application_type=APPLICATION_TYPE_NEW_LICENCE):
        date_filter = Application.get_activity_date_filter(
            for_application_type, 'selected_activities__')
        return Application.get_request_user_applications(request).filter(
            selected_activities__activity_status=ApplicationSelectedActivity.ACTIVITY_STATUS_CURRENT,
            **date_filter
        ).distinct()

    @staticmethod
    def get_request_user_applications(request):
        proxy_details = request.user.get_wildlifecompliance_proxy_details(request)
        proxy_id = proxy_details.get('proxy_id')
        organisation_id = proxy_details.get('organisation_id')
        return Application.objects.filter(
            Q(org_applicant_id=organisation_id) if organisation_id
            else (
                Q(submitter=proxy_id) | Q(proxy_applicant=proxy_id)
            ) if proxy_id
            else Q(submitter=request.user)
        )


class ApplicationInvoice(models.Model):
    application = models.ForeignKey(Application, related_name='invoices')
    invoice_reference = models.CharField(
        max_length=50, null=True, blank=True, default='')

    class Meta:
        app_label = 'wildlifecompliance'

    def __str__(self):
        return 'Application {} : Invoice #{}'.format(
            self.application_id, self.invoice_reference)

    # Properties
    # ==================
    @property
    def active(self):
        try:
            invoice = Invoice.objects.get(reference=self.invoice_reference)
            return False if invoice.voided else True
        except Invoice.DoesNotExist:
            pass
        return False


class ApplicationLogDocument(Document):
    log_entry = models.ForeignKey(
        'ApplicationLogEntry',
        related_name='documents')
    _file = models.FileField(upload_to=update_application_comms_log_filename)

    class Meta:
        app_label = 'wildlifecompliance'


class ApplicationLogEntry(CommunicationsLogEntry):
    application = models.ForeignKey(Application, related_name='comms_logs')

    class Meta:
        app_label = 'wildlifecompliance'

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.application.lodgement_number
        super(ApplicationLogEntry, self).save(**kwargs)


class ApplicationRequest(models.Model):
    application = models.ForeignKey(Application)
    subject = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    officer = models.ForeignKey(EmailUser, null=True)

    class Meta:
        app_label = 'wildlifecompliance'


class ReturnRequest(ApplicationRequest):
    RETURN_REQUEST_REASON_OUTSTANDING = 'outstanding'
    RETURN_REQUEST_REASON_OTHER = 'other'
    REASON_CHOICES = (
        (RETURN_REQUEST_REASON_OUTSTANDING, 'There are currently outstanding returns for the previous licence'),
        (RETURN_REQUEST_REASON_OTHER, 'Other')
    )
    reason = models.CharField(
        'Reason',
        max_length=30,
        choices=REASON_CHOICES,
        default=RETURN_REQUEST_REASON_OUTSTANDING)

    class Meta:
        app_label = 'wildlifecompliance'


class AmendmentRequest(ApplicationRequest):
    AMENDMENT_REQUEST_STATUS_REQUESTED = 'requested'
    AMENDMENT_REQUEST_STATUS_AMENDED = 'amended'
    STATUS_CHOICES = (
        (AMENDMENT_REQUEST_STATUS_REQUESTED, 'Requested'),
        (AMENDMENT_REQUEST_STATUS_AMENDED, 'Amended')
    )
    AMENDMENT_REQUEST_REASON_INSUFFICIENT_DETAIL = 'insufficient_detail'
    AMENDMENT_REQUEST_REASON_MISSING_INFO = 'missing_information'
    AMENDMENT_REQUEST_REASON_OTHER = 'other'
    REASON_CHOICES = (
        (AMENDMENT_REQUEST_REASON_INSUFFICIENT_DETAIL, 'The information provided was insufficient'),
        (AMENDMENT_REQUEST_REASON_MISSING_INFO, 'There was missing information'),
        (AMENDMENT_REQUEST_REASON_OTHER, 'Other')
    )
    status = models.CharField(
        'Status',
        max_length=30,
        choices=STATUS_CHOICES,
        default=AMENDMENT_REQUEST_STATUS_REQUESTED)
    reason = models.CharField(
        'Reason',
        max_length=30,
        choices=REASON_CHOICES,
        default=AMENDMENT_REQUEST_REASON_INSUFFICIENT_DETAIL)
    licence_activity = models.ForeignKey(
        'wildlifecompliance.LicenceActivity', null=True)

    class Meta:
        app_label = 'wildlifecompliance'

    def generate_amendment(self, request):
        with transaction.atomic():
            try:
                # This is to change the status of licence activity
                self.application.set_activity_processing_status(
                    self.licence_activity.id, ApplicationSelectedActivity.PROCESSING_STATUS_DRAFT)
                self.application.customer_status = Application.CUSTOMER_STATUS_AMENDMENT_REQUIRED
                self.application.save()

                # Create a log entry for the application
                self.application.log_user_action(
                    ApplicationUserAction.ACTION_ID_REQUEST_AMENDMENTS, request)
                self.save()
            except BaseException:
                raise


class Assessment(ApplicationRequest):
    STATUS_AWAITING_ASSESSMENT = 'awaiting_assessment'
    STATUS_ASSESSED = 'assessed'
    STATUS_COMPLETED = 'completed'
    STATUS_RECALLED = 'recalled'
    STATUS_CHOICES = (
        (STATUS_AWAITING_ASSESSMENT, 'Awaiting Assessment'),
        (STATUS_ASSESSED, 'Assessed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_RECALLED, 'Recalled')
    )
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_AWAITING_ASSESSMENT)
    date_last_reminded = models.DateField(null=True, blank=True)
    assessor_group = models.ForeignKey(
        ActivityPermissionGroup, null=False, default=1)
    licence_activity = models.ForeignKey(
        'wildlifecompliance.LicenceActivity', null=True)
    inspection_comment = models.TextField(blank=True)
    final_comment = models.TextField(blank=True)
    purpose = models.TextField(blank=True)
    inspection_date = models.DateField(null=True, blank=True)
    inspection_report = models.FileField(upload_to=update_assessment_inspection_report_filename, blank=True, null=True)
    actioned_by = models.ForeignKey(EmailUser, null=True)

    class Meta:
        app_label = 'wildlifecompliance'

    def generate_assessment(self, request):
        with transaction.atomic():
            try:
                # This is to change the status of licence activity
                self.application.set_activity_processing_status(
                    request.data.get('licence_activity'), ApplicationSelectedActivity.PROCESSING_STATUS_WITH_ASSESSOR)
                self.officer = request.user
                self.date_last_reminded = datetime.datetime.strptime(
                    timezone.now().strftime('%Y-%m-%d'), '%Y-%m-%d').date()
                self.save()

                select_group = self.assessor_group.members.all()

                # Create a log entry for the application
                self.application.log_user_action(
                    ApplicationUserAction.ACTION_SEND_FOR_ASSESSMENT_TO_.format(
                        self.assessor_group.name), request)
                # send email
                send_assessment_email_notification(select_group, self, request)
            except BaseException:
                raise

    def remind_assessment(self, request):
        with transaction.atomic():
            try:
                select_group = self.assessor_group.members.all()
                # send email
                send_assessment_reminder_email(select_group, self, request)
                self.date_last_reminded = datetime.datetime.strptime(
                    timezone.now().strftime('%Y-%m-%d'), '%Y-%m-%d').date()
                self.save()
                # Create a log entry for the application
                self.application.log_user_action(
                    ApplicationUserAction.ACTION_SEND_ASSESSMENT_REMINDER_TO_.format(
                        self.assessor_group.name), request)
            except BaseException:
                raise

    def recall_assessment(self, request):
        with transaction.atomic():
            try:
                self.status = Assessment.STATUS_RECALLED
                self.actioned_by = request.user
                self.save()

                if not Assessment.objects.filter(
                    application_id=self.application_id,
                    licence_activity=self.licence_activity_id,
                    status=Assessment.STATUS_AWAITING_ASSESSMENT
                ).exists():
                    # Create a log entry for the application
                    self.application.log_user_action(
                        ApplicationUserAction.ACTION_ASSESSMENT_RECALLED.format(
                            self.assessor_group), request)

                    last_complete_assessment = Assessment.objects.filter(
                        application_id=self.application_id,
                        licence_activity=self.licence_activity_id,
                        status=Assessment.STATUS_COMPLETED,
                        actioned_by__isnull=False
                    ).order_by('-id').first()
                    if last_complete_assessment:
                        last_complete_assessment.application.check_assessment_complete(self.licence_activity_id)
                    else:
                        self.application.set_activity_processing_status(
                            self.licence_activity_id,
                            ApplicationSelectedActivity.PROCESSING_STATUS_WITH_OFFICER
                        )

            except BaseException:
                raise

    def resend_assessment(self, request):
        with transaction.atomic():
            try:
                self.status = Assessment.STATUS_AWAITING_ASSESSMENT
                self.application.set_activity_processing_status(
                    self.licence_activity_id, ApplicationSelectedActivity.PROCESSING_STATUS_WITH_ASSESSOR)
                self.save()
                # Create a log entry for the application
                self.application.log_user_action(
                    ApplicationUserAction.ACTION_ASSESSMENT_RESENT.format(
                        self.assessor_group), request)
            except BaseException:
                raise

    @property
    def selected_activity(self):
        return ApplicationSelectedActivity.objects.filter(
            application_id=self.application_id,
            licence_activity_id=self.licence_activity_id
        ).first()

    @property
    def is_inspection_required(self):
        return self.selected_activity.is_inspection_required


class ApplicationSelectedActivity(models.Model):
    PROPOSED_ACTION_DEFAULT = 'default'
    PROPOSED_ACTION_DECLINE = 'propose_decline'
    PROPOSED_ACTION_ISSUE = 'propose_issue'
    PROPOSED_ACTION_CHOICES = (
        (PROPOSED_ACTION_DEFAULT, 'Default'),
        (PROPOSED_ACTION_DECLINE, 'Propose Decline'),
        (PROPOSED_ACTION_ISSUE, 'Propose Issue')
    )

    DECISION_ACTION_DEFAULT = 'default'
    DECISION_ACTION_DECLINED = 'declined'
    DECISION_ACTION_ISSUED = 'issued'
    DECISION_ACTION_CHOICES = (
        (DECISION_ACTION_DEFAULT, 'Default'),
        (DECISION_ACTION_DECLINED, 'Declined'),
        (DECISION_ACTION_ISSUED, 'Issued'),
    )

    ACTIVITY_STATUS_DEFAULT = 'default'
    ACTIVITY_STATUS_CURRENT = 'current'
    ACTIVITY_STATUS_EXPIRED = 'expired'
    ACTIVITY_STATUS_CANCELLED = 'cancelled'
    ACTIVITY_STATUS_SURRENDERED = 'surrendered'
    ACTIVITY_STATUS_SUSPENDED = 'suspended'
    ACTIVITY_STATUS_REPLACED = 'replaced'
    ACTIVITY_STATUS_CHOICES = (
        (ACTIVITY_STATUS_DEFAULT, 'Default'),
        (ACTIVITY_STATUS_CURRENT, 'Current'),
        (ACTIVITY_STATUS_EXPIRED, 'Expired'),
        (ACTIVITY_STATUS_CANCELLED, 'Cancelled'),
        (ACTIVITY_STATUS_SURRENDERED, 'Surrendered'),
        (ACTIVITY_STATUS_SUSPENDED, 'Suspended'),
        (ACTIVITY_STATUS_REPLACED, 'Replaced')
    )

    PROCESSING_STATUS_DRAFT = 'draft'
    PROCESSING_STATUS_WITH_OFFICER = 'with_officer'
    PROCESSING_STATUS_WITH_ASSESSOR = 'with_assessor'
    PROCESSING_STATUS_OFFICER_CONDITIONS = 'with_officer_conditions'
    PROCESSING_STATUS_OFFICER_FINALISATION = 'with_officer_finalisation'
    PROCESSING_STATUS_AWAITING_LICENCE_FEE_PAYMENT = 'awaiting_licence_fee_payment'
    PROCESSING_STATUS_ACCEPTED = 'accepted'
    PROCESSING_STATUS_DECLINED = 'declined'
    PROCESSING_STATUS_DISCARDED = 'discarded'
    PROCESSING_STATUS_CHOICES = (
        (PROCESSING_STATUS_DRAFT, 'Draft'),
        (PROCESSING_STATUS_WITH_OFFICER, 'With Officer'),
        (PROCESSING_STATUS_WITH_ASSESSOR, 'With Assessor'),
        (PROCESSING_STATUS_OFFICER_CONDITIONS, 'With Officer-Conditions'),
        (PROCESSING_STATUS_OFFICER_FINALISATION, 'With Officer-Finalisation'),
        (PROCESSING_STATUS_AWAITING_LICENCE_FEE_PAYMENT, 'Awaiting Licence Fee Payment'),
        (PROCESSING_STATUS_ACCEPTED, 'Accepted'),
        (PROCESSING_STATUS_DECLINED, 'Declined'),
        (PROCESSING_STATUS_DISCARDED, 'Discarded'),
    )
    proposed_action = models.CharField(
        'Action',
        max_length=20,
        choices=PROPOSED_ACTION_CHOICES,
        default=PROPOSED_ACTION_DEFAULT)
    decision_action = models.CharField(
        'Action',
        max_length=20,
        choices=DECISION_ACTION_CHOICES,
        default=DECISION_ACTION_DEFAULT)
    processing_status = models.CharField(
        'Processing Status',
        max_length=30,
        choices=PROCESSING_STATUS_CHOICES,
        default=PROCESSING_STATUS_DRAFT)
    activity_status = models.CharField(
        max_length=40,
        choices=ACTIVITY_STATUS_CHOICES,
        default=ACTIVITY_STATUS_DEFAULT)
    application = models.ForeignKey(Application, related_name='selected_activities')
    updated_by = models.ForeignKey(EmailUser, null=True)
    reason = models.TextField(blank=True)
    cc_email = models.TextField(null=True)
    activity = JSONField(blank=True, null=True)
    licence_activity = models.ForeignKey(
        'wildlifecompliance.LicenceActivity', null=True)
    proposed_start_date = models.DateField(null=True, blank=True)
    proposed_end_date = models.DateField(null=True, blank=True)
    additional_info = models.TextField(blank=True, null=True)
    conditions = models.TextField(blank=True, null=True)
    original_issue_date = models.DateTimeField(blank=True, null=True)
    issue_date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    is_inspection_required = models.BooleanField(default=False)
    licence_fee = models.DecimalField(
        max_digits=8, decimal_places=2, default='0')

    def __str__(self):
        return "Application {id} Selected Activity: {activity_id}".format(
            id=self.application_id,
            activity_id=self.licence_activity_id
        )

    class Meta:
        app_label = 'wildlifecompliance'

    @staticmethod
    def is_valid_status(status):
        return filter(lambda x: x[0] == status,
                      ApplicationSelectedActivity.PROCESSING_STATUS_CHOICES)

    @property
    def purposes(self):
        from wildlifecompliance.components.licences.models import LicencePurpose
        return LicencePurpose.objects.filter(
            application__id=self.application_id,
            licence_activity_id=self.licence_activity_id
        ).distinct()

    @property
    def current_purposes(self):
        '''
        need to clarify why ASA.purposes uses activity chain, should this be renamed to "current_purposes"?
        should there be a separate function that just returns the purposes for the individual ASA?
        after checking usage of .purposes, it seems maybe this was replaced by the creation of "current_activities"
        may not need this if current_activities is correct, then purposes for an ASA should always
        just show its own purposes, not full chain list
        '''

        from wildlifecompliance.components.licences.models import LicencePurpose
        activity_chain = self.application.get_activity_chain(
            licence_activity_id=self.licence_activity_id,
            activity_status=ApplicationSelectedActivity.ACTIVITY_STATUS_CURRENT
        )
        application_ids = set([activity.application_id for activity in activity_chain] + [self.application_id])
        return LicencePurpose.objects.filter(
            application__id__in=application_ids,
            licence_activity_id=self.licence_activity_id
        ).distinct()

    @property
    def can_amend(self):
        # Returns true if the activity can be included in a Amendment Application
        return ApplicationSelectedActivity.get_current_activities_for_application_type(
            Application.APPLICATION_TYPE_AMENDMENT,
            activity_ids=[self.id]
        ).count() > 0

    @property
    def can_renew(self):
        # Returns true if the activity can be included in a Renewal Application
        return ApplicationSelectedActivity.get_current_activities_for_application_type(
            Application.APPLICATION_TYPE_RENEWAL,
            activity_ids=[self.id]
        ).count() > 0

    @property
    def can_reactivate_renew(self):
        # TODO: clarify business logic for when an activity renew is allowed to be reactivate.
        return ApplicationSelectedActivity.get_current_activities_for_application_type(
            Application.APPLICATION_TYPE_NEW_LICENCE,
            activity_ids=[self.id]
        ).count() > 0

    @property
    def can_surrender(self):
        # TODO: clarify business logic for when an activity is allowed to be surrendered.
        return ApplicationSelectedActivity.get_current_activities_for_application_type(
            Application.APPLICATION_TYPE_NEW_LICENCE,
            activity_ids=[self.id]
        ).count() > 0

    @property
    def can_cancel(self):
        # TODO: clarify business logic for when an activity is allowed to be cancelled.
        return ApplicationSelectedActivity.get_current_activities_for_application_type(
            Application.APPLICATION_TYPE_NEW_LICENCE,
            activity_ids=[self.id]
        ).count() > 0

    @property
    def can_suspend(self):
        # TODO: clarify business logic for when an activity is allowed to be suspended.
        return ApplicationSelectedActivity.get_current_activities_for_application_type(
            Application.APPLICATION_TYPE_NEW_LICENCE,
            activity_ids=[self.id]
        ).count() > 0

    @property
    def can_reissue(self):
        # Returns true if the activity has expired, excluding if it was surrendered or cancelled
        current_date = timezone.now().date()
        return ApplicationSelectedActivity.objects.filter(
            Q(id=self.id, expiry_date__isnull=False),
            Q(expiry_date__lt=current_date) |
            Q(activity_status=ApplicationSelectedActivity.ACTIVITY_STATUS_EXPIRED)
        ).exclude(
            activity_status__in=[
                ApplicationSelectedActivity.ACTIVITY_STATUS_SURRENDERED,
                ApplicationSelectedActivity.ACTIVITY_STATUS_CANCELLED,
                ApplicationSelectedActivity.ACTIVITY_STATUS_REPLACED
            ]
        ).count() > 0

    @property
    def can_reinstate(self):
        # Returns true if the activity has not yet expired and is currently suspended
        current_date = timezone.now().date()
        return self.expiry_date and\
            self.expiry_date >= current_date and\
            self.activity_status == ApplicationSelectedActivity.ACTIVITY_STATUS_SUSPENDED

    @property
    def base_fees(self):
        return Application.calculate_base_fees(
            self.application.licence_purposes.filter(
                licence_activity_id=self.licence_activity_id
            ).values_list('id', flat=True)
        )

    @property
    def licence_fee_paid(self):
        return self.payment_status in [
            Invoice.PAYMENT_STATUS_NOT_REQUIRED,
            Invoice.PAYMENT_STATUS_PAID,
            Invoice.PAYMENT_STATUS_OVERPAID,
        ]

    @property
    def payment_status(self):
        if self.licence_fee == 0:
            return Invoice.PAYMENT_STATUS_NOT_REQUIRED
        else:
            if self.invoices.count() == 0:
                return Invoice.PAYMENT_STATUS_UNPAID
            else:
                try:
                    latest_invoice = Invoice.objects.get(
                        reference=self.invoices.latest('id').invoice_reference)
                except Invoice.DoesNotExist:
                    return Invoice.PAYMENT_STATUS_UNPAID
                return latest_invoice.payment_status

    @staticmethod
    def get_current_activities_for_application_type(application_type, **kwargs):
        applications = kwargs.get('applications', Application.objects.none())
        activity_ids = kwargs.get('activity_ids', [])

        date_filter = Application.get_activity_date_filter(
            application_type)
        return ApplicationSelectedActivity.objects.filter(
            Q(id__in=activity_ids) if activity_ids else
            Q(application_id__in=applications.values_list('id', flat=True)),
            **date_filter
        ).exclude(
            activity_status__in=[
                ApplicationSelectedActivity.ACTIVITY_STATUS_SURRENDERED,
                ApplicationSelectedActivity.ACTIVITY_STATUS_EXPIRED,
                ApplicationSelectedActivity.ACTIVITY_STATUS_CANCELLED,
                ApplicationSelectedActivity.ACTIVITY_STATUS_REPLACED
            ]
        ).distinct()

    def process_licence_fee_payment(self, request, application):
        from ledger.payments.models import BpointToken
        if self.licence_fee_paid:
            return True

        applicant = application.proxy_applicant if application.proxy_applicant else application.submitter
        card_owner_id = applicant.id
        card_token = BpointToken.objects.filter(user_id=card_owner_id).order_by('-id').first()
        if not card_token:
            logger.error("No card token found for user: %s" % card_owner_id)
            return False

        product_lines = []
        application_submission = u'Activity licence issued for {} application {}'.format(
            u'{} {}'.format(applicant.first_name, applicant.last_name), application.lodgement_number)
        set_session_application(request.session, application)
        product_lines.append({
            'ledger_description': '{}'.format(self.licence_activity.name),
            'quantity': 1,
            'price_incl_tax': str(self.licence_fee),
            'price_excl_tax': str(calculate_excl_gst(self.licence_fee)),
            'oracle_code': ''
        })
        checkout(
            request, application, lines=product_lines,
            invoice_text=application_submission,
            internal=True,
            add_checkout_params={
                'basket_owner': request.user.id,
                'payment_method': 'card',
                'checkout_token': card_token.id,
            }
        )
        try:
            invoice_ref = request.session['checkout_invoice']
        except KeyError:
            logger.error("No invoice reference generated for Activity ID: %s" % self.licence_activity_id)
            return False
        ActivityInvoice.objects.get_or_create(
            activity=self,
            invoice_reference=invoice_ref
        )
        delete_session_application(request.session)
        flush_checkout_session(request.session)
        return self.licence_fee_paid and send_activity_invoice_email_notification(application, self, invoice_ref, request)

    def reactivate_renew(self, request):
        pass
        # with transaction.atomic():
        #     self.activity_status = ApplicationSelectedActivity.ACTIVITY_STATUS_SURRENDERED
        #     self.updated_by = request.user
        #     self.save()

    def surrender(self, request):
        with transaction.atomic():
            self.activity_status = ApplicationSelectedActivity.ACTIVITY_STATUS_SURRENDERED
            self.updated_by = request.user
            self.save()

    def cancel(self, request):
        with transaction.atomic():
            self.activity_status = ApplicationSelectedActivity.ACTIVITY_STATUS_CANCELLED
            self.updated_by = request.user
            self.save()

    def suspend(self, request):
        with transaction.atomic():
            self.activity_status = ApplicationSelectedActivity.ACTIVITY_STATUS_SUSPENDED
            self.updated_by = request.user
            self.save()

    def reinstate(self, request):
        with transaction.atomic():
            self.activity_status = ApplicationSelectedActivity.ACTIVITY_STATUS_CURRENT
            self.updated_by = request.user
            self.save()


class ActivityInvoice(models.Model):
    activity = models.ForeignKey(ApplicationSelectedActivity, related_name='invoices')
    invoice_reference = models.CharField(
        max_length=50, null=True, blank=True, default='')

    class Meta:
        app_label = 'wildlifecompliance'

    def __str__(self):
        return 'Activity {} : Invoice #{}'.format(
            self.activity_id, self.invoice_reference)

    # Properties
    # ==================
    @property
    def active(self):
        try:
            invoice = Invoice.objects.get(reference=self.invoice_reference)
            return False if invoice.voided else True
        except Invoice.DoesNotExist:
            pass
        return False



@python_2_unicode_compatible
class ApplicationFormDataRecord(models.Model):

    INSTANCE_ID_SEPARATOR = "__instance-"

    ACTION_TYPE_ASSIGN_VALUE = 'value'
    ACTION_TYPE_ASSIGN_COMMENT = 'comment'

    COMPONENT_TYPE_TEXT = 'text'
    COMPONENT_TYPE_TAB = 'tab'
    COMPONENT_TYPE_SECTION = 'section'
    COMPONENT_TYPE_GROUP = 'group'
    COMPONENT_TYPE_NUMBER = 'number'
    COMPONENT_TYPE_EMAIL = 'email'
    COMPONENT_TYPE_SELECT = 'select'
    COMPONENT_TYPE_MULTI_SELECT = 'multi-select'
    COMPONENT_TYPE_TEXT_AREA = 'text_area'
    COMPONENT_TYPE_TABLE = 'table'
    COMPONENT_TYPE_EXPANDER_TABLE = 'expander_table'
    COMPONENT_TYPE_LABEL = 'label'
    COMPONENT_TYPE_RADIO = 'radiobuttons'
    COMPONENT_TYPE_CHECKBOX = 'checkbox'
    COMPONENT_TYPE_DECLARATION = 'declaration'
    COMPONENT_TYPE_FILE = 'file'
    COMPONENT_TYPE_DATE = 'date'
    COMPONENT_TYPE_CHOICES = (
        (COMPONENT_TYPE_TEXT, 'Text'),
        (COMPONENT_TYPE_TAB, 'Tab'),
        (COMPONENT_TYPE_SECTION, 'Section'),
        (COMPONENT_TYPE_GROUP, 'Group'),
        (COMPONENT_TYPE_NUMBER, 'Number'),
        (COMPONENT_TYPE_EMAIL, 'Email'),
        (COMPONENT_TYPE_SELECT, 'Select'),
        (COMPONENT_TYPE_MULTI_SELECT, 'Multi-Select'),
        (COMPONENT_TYPE_TEXT_AREA, 'Text Area'),
        (COMPONENT_TYPE_TABLE, 'Table'),
        (COMPONENT_TYPE_EXPANDER_TABLE, 'Expander Table'),
        (COMPONENT_TYPE_LABEL, 'Label'),
        (COMPONENT_TYPE_RADIO, 'Radio'),
        (COMPONENT_TYPE_CHECKBOX, 'Checkbox'),
        (COMPONENT_TYPE_DECLARATION, 'Declaration'),
        (COMPONENT_TYPE_FILE, 'File'),
        (COMPONENT_TYPE_DATE, 'Date'),
    )

    application = models.ForeignKey(Application, related_name='form_data_records')
    field_name = models.CharField(max_length=512, null=True, blank=True)
    schema_name = models.CharField(max_length=256, null=True, blank=True)
    instance_name = models.CharField(max_length=256, null=True, blank=True)
    component_type = models.CharField(
        max_length=64,
        choices=COMPONENT_TYPE_CHOICES,
        default=COMPONENT_TYPE_TEXT)
    value = JSONField(blank=True, null=True)
    officer_comment = models.TextField(blank=True)
    assessor_comment = models.TextField(blank=True)
    deficiency = models.TextField(blank=True)
    licence_activity = models.ForeignKey(LicenceActivity, related_name='form_data_records')

    def __str__(self):
        return "Application {id} record {field}".format(
            id=self.application_id,
            field=self.field_name
        )

    class Meta:
        app_label = 'wildlifecompliance'
        unique_together = ('application', 'field_name',)

    @staticmethod
    def process_form(request, application, form_data, action=ACTION_TYPE_ASSIGN_VALUE):
        from wildlifecompliance.components.applications.utils import MissingFieldsException
        can_edit_officer_comments = request.user.has_perm(
            'wildlifecompliance.licensing_officer'
        )
        can_edit_assessor_comments = request.user.has_perm(
            'wildlifecompliance.assessor'
        )
        can_edit_comments = can_edit_officer_comments or can_edit_assessor_comments
        can_edit_deficiencies = request.user.has_perm(
            'wildlifecompliance.licensing_officer'
        )

        if action == ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_COMMENT and\
                not can_edit_comments and not can_edit_deficiencies:
            raise Exception(
                'You are not authorised to perform this action!')

        is_draft = form_data.pop('__draft', False)
        visible_data_tree = application.get_visible_form_data_tree(form_data.items())
        required_fields = application.required_fields
        missing_fields = []

        for field_name, field_data in form_data.items():
            schema_name = field_data.get('schema_name', '')
            instance_name = field_data.get('instance_name', '')
            component_type = field_data.get('component_type', '')
            value = field_data.get('value', '')
            officer_comment = field_data.get('officer_comment', '')
            assessor_comment = field_data.get('assessor_comment', '')
            deficiency = field_data.get('deficiency_value', '')
            activity_id = field_data.get('licence_activity_id', '')

            if ApplicationFormDataRecord.INSTANCE_ID_SEPARATOR in field_name:
                [parsed_schema_name, parsed_instance_name] = field_name.split(
                    ApplicationFormDataRecord.INSTANCE_ID_SEPARATOR
                )
                schema_name = schema_name if schema_name else parsed_schema_name
                instance_name = instance_name if instance_name else parsed_instance_name

            try:
                visible_data_tree[instance_name][schema_name]
            except KeyError:
                continue

            form_data_record = ApplicationFormDataRecord.objects.filter(
                application_id=application.id,
                field_name=field_name,
                licence_activity_id=activity_id,
            ).first()

            if not form_data_record:
                form_data_record = ApplicationFormDataRecord.objects.create(
                    application_id=application.id,
                    field_name=field_name,
                    schema_name=schema_name,
                    instance_name=instance_name,
                    component_type=component_type,
                    licence_activity_id=activity_id
                )
            if action == ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_VALUE:
                if not is_draft and not value and schema_name in required_fields:
                    missing_item = {'field_name': field_name}
                    missing_item.update(required_fields[schema_name])
                    missing_fields.append(missing_item)
                    continue
                form_data_record.value = value
            elif action == ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_COMMENT:
                if can_edit_officer_comments:
                    form_data_record.officer_comment = officer_comment
                if can_edit_assessor_comments:
                    form_data_record.assessor_comment = assessor_comment
                if can_edit_deficiencies:
                    form_data_record.deficiency = deficiency
            form_data_record.save()

        if action == ApplicationFormDataRecord.ACTION_TYPE_ASSIGN_VALUE:
            application.update_dynamic_attributes()
            for existing_field in ApplicationFormDataRecord.objects.filter(application_id=application.id):
                if existing_field.field_name not in form_data.keys():
                    existing_field.delete()

        if missing_fields:
            raise MissingFieldsException(
                [{'name': item['field_name'], 'label': '{label}'.format(
                    label=item['label']
                )} for item in missing_fields]
            )


@python_2_unicode_compatible
class ApplicationStandardCondition(RevisionedMixin):
    text = models.TextField()
    code = models.CharField(max_length=10, unique=True)
    obsolete = models.BooleanField(default=False)
    return_type = models.ForeignKey('wildlifecompliance.ReturnType', null=True)

    def __str__(self):
        return self.code

    class Meta:
        app_label = 'wildlifecompliance'


class DefaultCondition(OrderedModel):
    condition = models.TextField(null=True, blank=True)
    licence_activity = models.ForeignKey(
        'wildlifecompliance.LicenceActivity', null=True)
    return_type = models.ForeignKey('wildlifecompliance.ReturnType', null=True)

    class Meta:
        app_label = 'wildlifecompliance'


class ApplicationCondition(OrderedModel):
    APPLICATION_CONDITION_RECURRENCE_WEEKLY = 'weekly'
    APPLICATION_CONDITION_RECURRENCE_MONTHLY = 'monthly'
    APPLICATION_CONDITION_RECURRENCE_YEARLY = 'yearly'
    RECURRENCE_PATTERNS = (
        (APPLICATION_CONDITION_RECURRENCE_WEEKLY, 'Weekly'),
        (APPLICATION_CONDITION_RECURRENCE_MONTHLY, 'Monthly'),
        (APPLICATION_CONDITION_RECURRENCE_YEARLY, 'Yearly')
    )
    standard_condition = models.ForeignKey(
        ApplicationStandardCondition, null=True, blank=True)
    free_condition = models.TextField(null=True, blank=True)
    default_condition = models.ForeignKey(
        DefaultCondition, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    standard = models.BooleanField(default=True)
    application = models.ForeignKey(Application, related_name='conditions')
    due_date = models.DateField(null=True, blank=True)
    recurrence = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(
        max_length=20,
        choices=RECURRENCE_PATTERNS,
        default=APPLICATION_CONDITION_RECURRENCE_WEEKLY)
    recurrence_schedule = models.IntegerField(null=True, blank=True)
    licence_activity = models.ForeignKey(
        'wildlifecompliance.LicenceActivity', null=True)
    return_type = models.ForeignKey('wildlifecompliance.ReturnType', null=True)
    # order = models.IntegerField(default=1)

    class Meta:
        app_label = 'wildlifecompliance'

    def submit(self):
        if self.standard:
            self.return_type = self.standard_condition.return_type
            self.save()

    @property
    def condition(self):
        if self.standard:
            return self.standard_condition.text
        elif self.is_default:
            return self.default_condition.condition
        else:
            return self.free_condition


class ApplicationUserAction(UserAction):
    ACTION_CREATE_CUSTOMER_ = "Create customer {}"
    ACTION_CREATE_PROFILE_ = "Create profile {}"
    ACTION_LODGE_APPLICATION = "Lodge application {}"
    ACTION_ASSIGN_TO_OFFICER = "Assign application {} to officer {}"
    ACTION_UNASSIGN_OFFICER = "Unassign officer from application {}"
    ACTION_ACCEPT_ID = "Accept ID"
    ACTION_RESET_ID = "Reset ID"
    ACTION_ID_REQUEST_UPDATE = 'Request ID update'
    ACTION_ACCEPT_CHARACTER = 'Accept character'
    ACTION_RESET_CHARACTER = "Reset character"
    ACTION_ACCEPT_REVIEW = 'Accept review'
    ACTION_RESET_REVIEW = "Reset review"
    ACTION_ID_REQUEST_AMENDMENTS = "Request amendments"
    ACTION_ID_REQUEST_AMENDMENTS_SUBMIT = "Amendment submitted by {}"
    ACTION_SEND_FOR_ASSESSMENT_TO_ = "Sent for assessment to {}"
    ACTION_SEND_ASSESSMENT_REMINDER_TO_ = "Send assessment reminder to {}"
    ACTION_ASSESSMENT_RECALLED = "Assessment recalled {}"
    ACTION_ASSESSMENT_RESENT = "Assessment Resent {}"
    ACTION_ASSESSMENT_COMPLETE = "Assessment Completed for group {} "
    ACTION_DECLINE = "Decline application {}"
    ACTION_ENTER_CONDITIONS = "Entered condition for activity {}"
    ACTION_CREATE_CONDITION_ = "Create condition {}"
    ACTION_ISSUE_LICENCE_ = "Issue Licence for activity {}"
    ACTION_DECLINE_LICENCE_ = "Decline Licence for activity {}"
    ACTION_DISCARD_APPLICATION = "Discard application {}"
    # Assessors
    ACTION_SAVE_ASSESSMENT_ = "Save assessment {}"
    ACTION_CONCLUDE_ASSESSMENT_ = "Conclude assessment {}"
    ACTION_PROPOSED_LICENCE = "Application {} has been proposed for licence"
    ACTION_PROPOSED_DECLINE = "Application {} has been proposed for decline"

    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, application, action, user):
        return cls.objects.create(
            application=application,
            who=user,
            what=str(action)
        )

    application = models.ForeignKey(Application, related_name='action_logs')


@receiver(pre_delete, sender=Application)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()
