from __future__ import unicode_literals
import logging
from django.db import models
from django.contrib.gis.db import models
from django.contrib.postgres.fields.jsonb import JSONField
from django.db.models import Max
from django.utils.encoding import python_2_unicode_compatible
from ledger.accounts.models import EmailUser, RevisionedMixin, Organisation
from ledger.licence.models import LicenceType
from wildlifecompliance.components.main.models import CommunicationsLogEntry, UserAction, Document
from wildlifecompliance.components.organisations.models import Organisation
from wildlifecompliance.components.call_email.models import CallEmail
from wildlifecompliance.components.main.models import CommunicationsLogEntry,\
    UserAction, Document, get_related_items
from wildlifecompliance.components.users.models import RegionDistrict, CompliancePermissionGroup
from wildlifecompliance.components.main.models import InspectionType
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

def update_inspection_comms_log_filename(instance, filename):
    return 'wildlifecompliance/compliance/{}/communications/{}/{}'.format(
        instance.log_entry.inspection.id, instance.id, filename)


class Inspection(RevisionedMixin):
    PARTY_CHOICES = (
            ('individual', 'individual'),
            ('organisation', 'organisation')
            )
    STATUS_CHOICES = (
            ('open', 'Open'),
            ('endorsement', 'Awaiting Endorsement'),
            ('sanction_outcome', 'Awaiting Sanction Outcomes'),
            ('discarded', 'Discarded'),
            ('closed', 'Closed')
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
            related_name='inspection_type',
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
        return self.id

    @property
    def get_related_items_descriptor(self):
        return '{0}, {1}'.format(self.title, self.details)
    

class InspectionCommsLogDocument(Document):
    log_entry = models.ForeignKey(
        'InspectionCommsLogEntry',
        related_name='documents')
    _file = models.FileField(max_length=255, upload_to=update_inspection_comms_log_filename)

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
