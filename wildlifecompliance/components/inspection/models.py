from __future__ import unicode_literals
import logging
from django.db import models
from django.contrib.gis.db import models
from django.contrib.postgres.fields.jsonb import JSONField
from django.db.models import Max
from django.utils.encoding import python_2_unicode_compatible
from ledger.accounts.models import EmailUser, RevisionedMixin, Organisation
from ledger.licence.models import LicenceType
from wildlifecompliance.components.organisations.models import Organisation
from wildlifecompliance.components.call_email.models import CallEmail
from wildlifecompliance.components.main.models import CommunicationsLogEntry,\
    UserAction, Document, get_related_items
from wildlifecompliance.components.users.models import RegionDistrict, CompliancePermissionGroup
#from wildlifecompliance.components.main.models import InspectionType
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

def update_inspection_comms_log_filename(instance, filename):
    #return 'wildlifecompliance/compliance/{}/communications/{}/{}'.format(
     #   instance.log_entry.inspection.id, instance.id, filename)
     pass

def update_inspection_report_filename(instance, filename):
    #return 'wildlifecompliance/compliance/{}/report/{}'.format(
     #   instance.id, filename)
     pass


class InspectionType(models.Model):
    inspection_type = models.CharField(max_length=50)
    schema = JSONField(null=True)
    version = models.SmallIntegerField(default=1, blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    replaced_by = models.ForeignKey(
        'self', on_delete=models.PROTECT, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    approval_document = models.ForeignKey(
        'InspectionTypeApprovalDocument',
        related_name='inspection_type',
        null=True)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_InspectionType'
        verbose_name_plural = 'CM_InspectionTypes'
        unique_together = ('inspection_type', 'version')

    def __str__(self):
        return '{0}, v.{1}'.format(self.inspection_type, self.version)


class Inspection(RevisionedMixin):
    PARTY_INDIVIDUAL = 'individual'
    PARTY_ORGANISATION = 'organisation'
    PARTY_CHOICES = (
            (PARTY_INDIVIDUAL, 'individual'),
            (PARTY_ORGANISATION, 'organisation')
            )
    STATUS_OPEN = 'open'
    STATUS_WITH_MANAGER = 'with_manager'
    STATUS_REQUEST_AMENDMENT = 'request_amendment'
    STATUS_ENDORSEMENT = 'endorsement'
    STATUS_SANCTION_OUTCOME = 'sanction_outcome'
    STATUS_DISCARDED = 'discarded'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = (
            (STATUS_OPEN, 'Open'),
            (STATUS_WITH_MANAGER, 'With Manager'),
            (STATUS_REQUEST_AMENDMENT, 'Request Amendment'),
            (STATUS_ENDORSEMENT, 'Awaiting Endorsement'),
            (STATUS_SANCTION_OUTCOME, 'Awaiting Sanction Outcomes'),
            (STATUS_DISCARDED, 'Discarded'),
            (STATUS_CLOSED, 'Closed')
            )

    title = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(
            max_length=100,
            choices=STATUS_CHOICES,
            default='open'
            )

    details = models.TextField(blank=True, null=True)
    number = models.CharField(max_length=50, blank=True, null=True)
    planned_for_date = models.DateField(null=True)
    planned_for_time = models.TimeField(blank=True, null=True)
    inform_party_being_inspected = models.BooleanField(default=False)
    party_inspected = models.CharField(
            max_length=30,
            choices=PARTY_CHOICES,
            default='individual'
            )
    call_email = models.ForeignKey(
        CallEmail, 
        related_name='inspection_call_email',
        null=True
        )
    individual_inspected = models.ForeignKey(
        EmailUser, 
        related_name='individual_inspected',
        null=True
        )
    organisation_inspected = models.ForeignKey(
        Organisation, 
        related_name='organisation_inspected',
        null=True
        )
    assigned_to = models.ForeignKey(
        EmailUser, 
        related_name='inspection_assigned_to',
        null=True
        )
    allocated_group = models.ForeignKey(
        CompliancePermissionGroup,
        related_name='inspection_allocated_group', 
        null=True
        )
    inspection_team = models.ManyToManyField(
        EmailUser,
        related_name='inspection_team',
        blank=True
        )
    inspection_team_lead = models.ForeignKey(
        EmailUser,
        related_name='inspection_team_lead',
        null=True
    )
    inspection_type = models.ForeignKey(
            InspectionType,
            related_name='inspection_inspection_type',
            null=True
            )

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Inspection'
        verbose_name_plural = 'CM_Inspections'

    def __str__(self):
        return 'ID: {0}, Type: {1}, Title: {2}' \
            .format(self.id, self.title, self.title)

    def clean(self):
        if self.individual_inspected and self.organisation_inspected:
            raise ValidationError('An inspection must target an individual or organisation, not both')

        super(Inspection, self).clean()
    
    # Prefix "IN" char to Inspection number.
    def save(self, *args, **kwargs):
        
        super(Inspection, self).save(*args,**kwargs)
        if self.number is None:
            new_number_id = 'IN{0:06d}'.format(self.pk)
            self.number = new_number_id
            self.save()
        
    def log_user_action(self, action, request):
        return InspectionUserAction.log_action(self, action, request.user)
    
    @property
    def get_related_items_identifier(self):
        return self.number

    @property
    def get_related_items_descriptor(self):
        return '{0}, {1}'.format(self.title, self.details)

    @property
    def schema(self):
        
        if self.inspection_type:
            return self.inspection_type.schema

    def send_to_manager(self, request):
        self.status = self.STATUS_WITH_MANAGER
        self.log_user_action(
            InspectionUserAction.ACTION_SEND_TO_MANAGER.format(self.number), 
            request)
        self.save()

    def request_amendment(self, request):
        self.status = self.REQUEST_AMENDMENT
        self.log_user_action(
            InspectionUserAction.ACTION_REQUEST_AMENDMENT.format(self.number), 
            request)
        self.save()

    def close(self, request):
        self.status = self.STATUS_CLOSED
        self.log_user_action(
            InspectionUserAction.ACTION_CLOSED.format(self.number), 
            request)
        self.save()

class InspectionReportDocument(Document):
    log_entry = models.ForeignKey(
        'Inspection',
        related_name='report')
    _file = models.FileField(max_length=255)

    class Meta:
        app_label = 'wildlifecompliance'


class InspectionTypeApprovalDocument(Document):
    _file = models.FileField(max_length=255)

    class Meta:
        app_label = 'wildlifecompliance'


class InspectionCommsLogDocument(Document):
    log_entry = models.ForeignKey(
        'InspectionCommsLogEntry',
        related_name='documents')
    _file = models.FileField(max_length=255)

    class Meta:
        app_label = 'wildlifecompliance'


class InspectionCommsLogEntry(CommunicationsLogEntry):
    inspection = models.ForeignKey(Inspection, related_name='comms_logs')

    class Meta:
        app_label = 'wildlifecompliance'


class InspectionUserAction(UserAction):
    ACTION_SAVE_INSPECTION_ = "Save Inspection {}"
    ACTION_OFFENCE = "Create Offence {}"
    ACTION_SANCTION_OUTCOME = "Create Sanction Outcome {}"
    ACTION_SEND_TO_MANAGER = "Send Inspection {} to Manager"
    ACTION_CLOSED = "Close Inspection {}"
    ACTION_REQUEST_AMENDMENT = "Request amendment for {}"

    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, inspection, action, user):
        return cls.objects.create(
            inspection=inspection,
            who=user,
            what=str(action)
        )

    inspection = models.ForeignKey(Inspection, related_name='action_logs')


class InspectionDocument(Document):
    inspection = models.ForeignKey('Inspection', related_name='documents')
    _file = models.FileField(max_length=255)
    input_name = models.CharField(max_length=255, blank=True, null=True)
    # after initial submit prevent document from being deleted
    can_delete = models.BooleanField(default=True)
    version_comment = models.CharField(max_length=255, blank=True, null=True)

    def delete(self):
        if self.can_delete:
            return super(InspectionDocument, self).delete()
        #logger.info(
         #   'Cannot delete existing document object after application has been submitted (including document submitted before\
          #  application pushback to status Draft): {}'.format(
           #     self.name)
        #)

    class Meta:
        app_label = 'wildlifecompliance'

