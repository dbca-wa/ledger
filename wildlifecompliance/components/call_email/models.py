from __future__ import unicode_literals
import logging
from django.db import models
from django.contrib.gis.db import models
from django.contrib.postgres.fields.jsonb import JSONField
from django.db.models import Max
from django.utils.encoding import python_2_unicode_compatible
from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.licence.models import LicenceType
from wildlifecompliance.components.main.models import CommunicationsLogEntry, UserAction, Document
from wildlifecompliance.components.organisations.models import Organisation
from wildlifecompliance.components.applications.models import Application
from wildlifecompliance.components.main.models import CommunicationsLogEntry,\
    UserAction, Document


logger = logging.getLogger(__name__)


def update_compliance_doc_filename(instance, filename):
    return 'wildlifecompliance/compliance/{}/documents/{}'.format(
        instance.call_email.id, filename)


def update_compliance_comms_log_filename(instance, filename):
    return 'wildlifecompliance/compliance/{}/communications/{}/{}'.format(
        instance.log_entry.call_email.id, instance.id, filename)


class Classification(models.Model):
    NAME_CHOICES = (
        ('complaint', 'Complaint'),
        ('enquiry', 'Enquiry'),
        ('incident', 'Incident'),
    )

    name = models.CharField(
        max_length=30,
        choices=NAME_CHOICES,
        default='complaint'
    )

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Classification'
        verbose_name_plural = 'CM_Classifications'

    def __str__(self):
        return self.get_name_display()


class ReportType(models.Model):

    report_type = models.CharField(max_length=50)
    schema = JSONField(null=True)
    version = models.SmallIntegerField(default=1, blank=False, null=False)
    description = models.CharField(max_length=256, blank=True, null=True)
    replaced_by = models.ForeignKey(
        'self', on_delete=models.PROTECT, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_ReportType'
        verbose_name_plural = 'CM_ReportTypes'
        unique_together = ('report_type', 'version')

    def __str__(self):
        return '{0}, v.{1}'.format(self.report_type, self.version)


class Referrer(models.Model):
    name = models.CharField(max_length=50, blank=True)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Referrer'
        verbose_name_plural = 'CM_Referrers'

    def __str__(self):
        return self.name


class Location(models.Model):

    STATE_CHOICES = (
        ('WA', 'Western Australia'),
        ('VIC', 'Victoria'),
        ('QLD', 'Queensland'),
        ('NSW', 'New South Wales'),
        ('TAS', 'Tasmania'),
        ('NT', 'Northern Territory'),
        ('ACT', 'Australian Capital Territory')
    )

    # latitude = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    # longitude = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    wkb_geometry = models.PointField(srid=4326, blank=True, null=True)
    street = models.CharField(max_length=100, null=True, blank=True)
    town_suburb = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(
        max_length=50, choices=STATE_CHOICES, null=True, blank=True, default='WA')
    postcode = models.IntegerField(null=True)
    country = models.CharField(max_length=100, null=True, blank=True, default='Australia')
    objects = models.GeoManager()
    # call_email = models.ForeignKey(
    #     CallEmail,
    #     null=True,
    #     related_name="call_location"
    # )

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Location'
        verbose_name_plural = 'CM_Locations'

    def __str__(self):
        return '{0}, {1}, {2}' \
            .format(self.street, self.town_suburb, self.state)


class CallEmail(RevisionedMixin):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('open_followup', 'Open (follow-up)'),
        ('open_inspection', 'Open (Inspection)'),
        ('open_case', 'Open (Case)'),
        ('closed', 'Closed'),
    )

    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        default='draft')
    location = models.ForeignKey(
        Location,
        null=True,
        related_name="location_call"
    )
    classification = models.ForeignKey(
        Classification,
        related_name="classification_call"
    )
    schema = JSONField(default=list)
    lodged_on = models.DateField(auto_now_add=True)
    number = models.CharField(max_length=50, blank=True, null=True)
    caller = models.CharField(max_length=100, blank=True, null=True)
    assigned_to = models.CharField(max_length=100, blank=True, null=True)
    anonymous_call = models.BooleanField(default=False)
    caller_wishes_to_remain_anonymous = models.BooleanField(default=False)
    occurrence_date_from = models.DateField(null=True)
    occurrence_time_from = models.TimeField(null=True)
    occurrence_date_to = models.DateField(null=True)
    occurrence_time_to = models.TimeField(null=True)
    report_type = models.ForeignKey(
        ReportType,
        null=True
    )

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Call/Email'
        verbose_name_plural = 'CM_Calls/Emails'

    def __str__(self):
        return 'ID: {0}, Status: {1}, Number: {2}, Caller: {3}, Assigned To: {4}' \
            .format(self.id, self.status, self.number, self.caller, self.assigned_to)

    # Prefix Classification type char to CallEmail number.
    def save(self, *args, **kwargs):
        classification_instance = Classification.objects.get(id=self.classification_id)
        classification_prefix = classification_instance.name[0]
        
        super(CallEmail, self).save(*args,**kwargs)
        if self.number is None:
            new_number_id = '{0}{1:06d}'.format(classification_prefix, self.pk)
            self.number = new_number_id
            self.save()
        
    @property
    def data(self):
        """ returns a queryset of form data records attached to CallEmail (shortcut to ComplianceFormDataRecord related_name). """
        return self.form_data_records.all()
    
    def log_user_action(self, action, request):
        return ComplianceUserAction.log_action(self, action, request.user)


@python_2_unicode_compatible
class ComplianceFormDataRecord(models.Model):

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

    call_email = models.ForeignKey(CallEmail, related_name='form_data_records')
    field_name = models.CharField(max_length=512, null=True, blank=True)
    schema_name = models.CharField(max_length=256, null=True, blank=True)
    instance_name = models.CharField(max_length=256, null=True, blank=True)
    component_type = models.CharField(
        max_length=64,
        choices=COMPONENT_TYPE_CHOICES,
        default=COMPONENT_TYPE_TEXT)
    value = JSONField(blank=True, null=True)
    comment = models.TextField(blank=True)
    deficiency = models.TextField(blank=True)

    def __str__(self):
        return "CallEmail {id} record {field}: {value}".format(
            id=self.call_email_id,
            field=self.field_name,
            value=self.value[:8]
        )

    class Meta:
        app_label = 'wildlifecompliance'
        unique_together = ('call_email', 'field_name',)

    @staticmethod
    def process_form(request, CallEmail, form_data, action=ACTION_TYPE_ASSIGN_VALUE):
        print(form_data)
        can_edit_comments = request.user.has_perm(
            'wildlifecompliance.licensing_officer'
        ) or request.user.has_perm(
            'wildlifecompliance.assessor'
        )
        can_edit_deficiencies = request.user.has_perm(
            'wildlifecompliance.licensing_officer'
        )

        if action == ComplianceFormDataRecord.ACTION_TYPE_ASSIGN_COMMENT and\
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

            if ComplianceFormDataRecord.INSTANCE_ID_SEPARATOR in field_name:
                [parsed_schema_name, instance_name] = field_name.split(
                    ComplianceFormDataRecord.INSTANCE_ID_SEPARATOR
                )
                schema_name = schema_name if schema_name else parsed_schema_name

            form_data_record, created = ComplianceFormDataRecord.objects.get_or_create(
                call_email_id=CallEmail.id,
                field_name=field_name
            )
            if created:
                form_data_record.schema_name = schema_name
                form_data_record.instance_name = instance_name
                form_data_record.component_type = component_type
            if action == ComplianceFormDataRecord.ACTION_TYPE_ASSIGN_VALUE:
                form_data_record.value = value
            elif action == ComplianceFormDataRecord.ACTION_TYPE_ASSIGN_COMMENT:
                if can_edit_comments:
                    form_data_record.comment = comment
                if can_edit_deficiencies:
                    form_data_record.deficiency = deficiency
            form_data_record.save()


class ComplianceDocument(Document):
    call_email = models.ForeignKey('CallEmail', related_name='documents')
    _file = models.FileField(upload_to=update_compliance_doc_filename)
    input_name = models.CharField(max_length=255, null=True, blank=True)
    # after initial submit prevent document from being deleted
    can_delete = models.BooleanField(default=True)
    version_comment = models.CharField(max_length=255, null=True, blank=True)

    def delete(self):
        if self.can_delete:
            return super(ComplianceDocument, self).delete()
        logger.info(
            'Cannot delete existing document object after application has been submitted (including document submitted before\
            application pushback to status Draft): {}'.format(
                self.name)
        )

    class Meta:
        app_label = 'wildlifecompliance'


class ComplianceLogDocument(Document):
    log_entry = models.ForeignKey(
        'ComplianceLogEntry',
        related_name='documents')
    _file = models.FileField(upload_to=update_compliance_comms_log_filename)

    class Meta:
        app_label = 'wildlifecompliance'


class ComplianceLogEntry(CommunicationsLogEntry):
    call_email = models.ForeignKey(CallEmail, related_name='comms_logs')

    class Meta:
        app_label = 'wildlifecompliance'

    # def save(self, **kwargs):
        # save the application reference if the reference not provided
        # if not self.reference:
        #   self.reference = self.application.reference
        # super(ComplianceLogEntry, self).save(**kwargs)


class ComplianceUserAction(UserAction):
    ACTION_CHANGE_CLASSIFICATION_ = "Change Classification {}"

    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, call_email, action, user):
        return cls.objects.create(
            call_email=call_email,
            who=user,
            what=str(action)
        )

    call_email = models.ForeignKey(CallEmail, related_name='action_logs')
