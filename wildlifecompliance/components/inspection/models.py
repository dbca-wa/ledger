from __future__ import unicode_literals
import logging
from django.db import models
from django.contrib.gis.db import models
from django.contrib.postgres.fields.jsonb import JSONField
from django.db.models import Max
from django.utils.encoding import python_2_unicode_compatible
from ledger.accounts.models import EmailUser, RevisionedMixin, Organisation
from ledger.licence.models import LicenceType
#from wildlifecompliance.components.organisations.models import Organisation
from wildlifecompliance.components.call_email.models import CallEmail
from wildlifecompliance.components.main.models import (
        CommunicationsLogEntry,
        UserAction, 
        Document,
        )
#from wildlifecompliance.components.main.related_items_utils import get_related_items
from wildlifecompliance.components.users.models import RegionDistrict, CompliancePermissionGroup
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
    #STATUS_WITH_MANAGER = 'with_manager'
    #STATUS_REQUEST_AMENDMENT = 'request_amendment'
    STATUS_AWAIT_ENDORSEMENT = 'await_endorsement'
    #STATUS_SANCTION_OUTCOME = 'sanction_outcome'
    STATUS_DISCARDED = 'discarded'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = (
            (STATUS_OPEN, 'Open'),
            #(STATUS_WITH_MANAGER, 'With Manager'),
            #(STATUS_REQUEST_AMENDMENT, 'Request Amendment'),
            (STATUS_AWAIT_ENDORSEMENT, 'Awaiting Endorsement'),
            #(STATUS_SANCTION_OUTCOME, 'Awaiting Sanction Outcomes'),
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
        # related_name='inspection_team',
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
    region = models.ForeignKey(
        RegionDistrict, 
        related_name='inspection_region', 
        null=True
    )
    district = models.ForeignKey(
        RegionDistrict, 
        related_name='inspection_district', 
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
        
    @property
    def data(self):
        """ returns a queryset of form data records attached to Inspection (shortcut to InspectionFormDataRecord related_name). """
        return self.form_data_records.all()

    def log_user_action(self, action, request):
        return InspectionUserAction.log_action(self, action, request.user)
    
    @property
    def get_related_items_identifier(self):
        return self.number

    @property
    def get_related_items_descriptor(self):
        #return '{0}, {1}'.format(self.title, self.details)
        return self.title

    @property
    def schema(self):
        
        if self.inspection_type:
            return self.inspection_type.schema

    def send_to_manager(self, request):
        self.status = self.STATUS_AWAIT_ENDORSEMENT
        self.log_user_action(
            InspectionUserAction.ACTION_SEND_TO_MANAGER.format(self.number), 
            request)
        self.save()

    def request_amendment(self, request):
        self.status = self.STATUS_OPEN
        self.log_user_action(
            InspectionUserAction.ACTION_REQUEST_AMENDMENT.format(self.number), 
            request)
        self.save()

    # def endorsement(self, request):
    #     self.status = self.STATUS_ENDORSEMENT
    #     self.log_user_action(
    #         InspectionUserAction.ACTION_ENDORSEMENT.format(self.number), 
    #         request)
    #     self.save()

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
    ACTION_CREATE_INSPECTION = "Create Inspection {}"
    ACTION_SAVE_INSPECTION_ = "Save Inspection {}"
    ACTION_OFFENCE = "Create Offence {}"
    ACTION_SANCTION_OUTCOME = "Create Sanction Outcome {}"
    ACTION_SEND_TO_MANAGER = "Send Inspection {} to Manager"
    ACTION_CLOSED = "Close Inspection {}"
    ACTION_REQUEST_AMENDMENT = "Request amendment for {}"
    ACTION_ENDORSEMENT = "Endorse {}"
    # ACTION_ADD_WEAK_LINK = "Create manual link between Inspection: {} and {}: {}"
    # ACTION_REMOVE_WEAK_LINK = "Remove manual link between Inspection: {} and {}: {}"
    ACTION_ADD_WEAK_LINK = "Create manual link between {}: {} and {}: {}"
    ACTION_REMOVE_WEAK_LINK = "Remove manual link between {}: {} and {}: {}"
    ACTION_MAKE_TEAM_LEAD = "Make {} team lead"
    ACTION_ADD_TEAM_MEMBER = "Add {} to team"
    ACTION_REMOVE_TEAM_MEMBER = "Remove {} from team"
    ACTION_UPLOAD_INSPECTION_REPORT = "Upload Inspection Report '{}'"

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


@python_2_unicode_compatible
class InspectionFormDataRecord(models.Model):

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

    inspection = models.ForeignKey(Inspection, related_name='form_data_records')
    field_name = models.CharField(max_length=512, blank=True, null=True)
    schema_name = models.CharField(max_length=256, blank=True, null=True)
    instance_name = models.CharField(max_length=256, blank=True, null=True)
    component_type = models.CharField(
        max_length=64,
        choices=COMPONENT_TYPE_CHOICES,
        default=COMPONENT_TYPE_TEXT)
    value = JSONField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    deficiency = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Inspection {id} record {field}: {value}".format(
            id=self.inspection_id,
            field=self.field_name,
            value=self.value[:8]
        )

    class Meta:
        app_label = 'wildlifecompliance'
        unique_together = ('inspection', 'field_name',)

    @staticmethod
    def process_form(request, Inspection, form_data, action=ACTION_TYPE_ASSIGN_VALUE):
        can_edit_comments = request.user.has_perm(
            'wildlifecompliance.licensing_officer'
        ) or request.user.has_perm(
            'wildlifecompliance.assessor'
        )
        can_edit_deficiencies = request.user.has_perm(
            'wildlifecompliance.licensing_officer'
        )

        if action == InspectionFormDataRecord.ACTION_TYPE_ASSIGN_COMMENT and\
                not can_edit_comments and not can_edit_deficiencies:
            raise Exception(
                'You are not authorised to perform this action!')
        
        for field_name, field_data in form_data.items():
            schema_name = field_data.get('schema_name', '')
            component_type = field_data.get('component_type', '')
            value = field_data.get('value', '')
            comment = field_data.get('comment_value', '')
            deficiency = field_data.get('deficiency_value', '')
            instance_name = ''

            if InspectionFormDataRecord.INSTANCE_ID_SEPARATOR in field_name:
                [parsed_schema_name, instance_name] = field_name.split(
                    InspectionFormDataRecord.INSTANCE_ID_SEPARATOR
                )
                schema_name = schema_name if schema_name else parsed_schema_name

            form_data_record, created = InspectionFormDataRecord.objects.get_or_create(
                inspection_id=Inspection.id,
                field_name=field_name
            )
            if created:
                form_data_record.schema_name = schema_name
                form_data_record.instance_name = instance_name
                form_data_record.component_type = component_type
            if action == InspectionFormDataRecord.ACTION_TYPE_ASSIGN_VALUE:
                form_data_record.value = value
            elif action == InspectionFormDataRecord.ACTION_TYPE_ASSIGN_COMMENT:
                if can_edit_comments:
                    form_data_record.comment = comment
                if can_edit_deficiencies:
                    form_data_record.deficiency = deficiency
            form_data_record.save()


