from django.core.exceptions import ValidationError
from django.db import models
from ledger.accounts.models import RevisionedMixin, EmailUser, Organisation
from wildlifecompliance.components.call_email.models import Location, CallEmail
from wildlifecompliance.components.main.models import Document
from wildlifecompliance.components.users.models import RegionDistrict


class SectionRegulation(RevisionedMixin):
    act = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=50, blank=True, verbose_name='Regulation')
    offence_text = models.CharField(max_length=200, blank=True)
    amount =  models.DecimalField(max_digits=8, decimal_places=2, default='0.00')


    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Section/Regulation'
        verbose_name_plural = 'CM_Sections/Regulations'
        ordering = ('act', 'name')

    def __str__(self):
        return '{}:{}:{}'.format(self.act, self.name, self.offence_text)


class Offence(RevisionedMixin):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closing', 'Closing'),
        ('closed', 'Closed'),
    )

    identifier = models.CharField(
        max_length=50,
        blank=True,
    )
    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        default='draft',
    )
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        related_name="offence_location",
    )
    call_email = models.ForeignKey(
        CallEmail,
        null=True,
        blank=True,
        related_name='offence_call_eamil',
    )
    occurrence_from_to = models.BooleanField(default=False)
    occurrence_date_from = models.DateField(null=True, blank=True)
    occurrence_time_from = models.TimeField(null=True, blank=True)
    occurrence_date_to = models.DateField(null=True, blank=True)
    occurrence_time_to = models.TimeField(null=True, blank=True)
    alleged_offences = models.ManyToManyField(
        SectionRegulation,
        blank=True,
    )
    details = models.TextField(blank=True)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Offence'
        verbose_name_plural = 'CM_Offences'

    def __str__(self):
        return 'ID: {}, Status: {}, Identifier: {}'.format(self.id, self.status, self.identifier)
    
    @property
    def get_related_items_identifier(self):
        return '{}'.format(self.identifier)
    
    @property
    def get_related_items_descriptor(self):
        return '{}'.format(self.details)


class Offender(models.Model):
    reason_for_removal = models.TextField(blank=True)
    removed = models.BooleanField(default=False)
    removed_by = models.ForeignKey(
        EmailUser,
        null=True,
        related_name='offender_removed_by'
    )
    person = models.ForeignKey(
        EmailUser,
        null=True,
        related_name='offender_person',
    )
    organisation = models.ForeignKey(
        Organisation,
        null=True,
        related_name='offender_organisation',
    )
    offence = models.ForeignKey(
        Offence,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Offender'
        verbose_name_plural = 'CM_Offenders'

    def __str__(self):
        return 'First name: {}, Last name: {}'.format(self.person.first_name, self.person.last_name)


class SanctionOutcome(models.Model):
    TYPE_CHOICES = (
        ('infringement_notice', 'Infringement Notice'),
        ('caution_notice', 'Caution Notice'),
        ('letter_of_advice', 'Letter of Advice'),
        ('remediation_notice', 'Remediation Notice'),
    )

    type = models.CharField(max_length=30, choices=TYPE_CHOICES, blank=True,)
    region = models.ForeignKey(RegionDistrict, related_name='sanction_outcome_region', null=True,)
    district = models.ForeignKey(RegionDistrict, related_name='sanction_outcome_district', null=True,)
    identifier = models.CharField(max_length=50, blank=True,)
    offence = models.ForeignKey(Offence, related_name='sanction_outcome_offence', null=True, on_delete=models.SET_NULL,)
    offender = models.ForeignKey(Offender, related_name='sanction_outcome_offender', null=True, on_delete=models.SET_NULL,)
    alleged_offences = models.ManyToManyField(SectionRegulation, blank=True, related_name='sanction_outcome_alleged_offences')

    issued_on_paper = models.BooleanField(default=False) # This is always true when type is letter_of_advice
    paper_id = models.CharField(max_length=50, blank=True,)

    description = models.TextField(blank=True)

    # Only editable when issued on paper. Otherwise pre-filled with date/time when issuing electronically.
    date_of_issue = models.DateField(null=True, blank=True)
    time_of_issue = models.TimeField(null=True, blank=True)

    def clean(self):
        if self.offender and not self.offence:
            raise ValidationError('An offence must be selected to save offender(s).')

        if self.alleged_offences.all().count() and not self.offence:
            raise ValidationError('An offence must be selected to save alleged offence(s).')

        # validate if offender is registered under the offence
        if self.offender not in self.offence.offence_set:
            raise ValidationError('Offender must be registered under the selected offence.')

        # validate if alleged_offences are registered under the offence
        for alleged_offence in self.alleged_offences:
            if alleged_offence not in self.offence.alleged_offences:
                raise ValidationError('Alleged offence must be registered under the selected offence.')

        # make issued_on_papaer true whenever the type is letter_of_advice
        if self.type == 'letter_of_advice':
            self.issued_on_paper = True

        super(SanctionOutcome, self).clean()

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_SanctionOutcome'
        verbose_name_plural = 'CM_SanctionOutcomes'

    def __str__(self):
        return 'Type : {}, Identifier: {}'.format(self.type, self.identifier)


class RemediationAction(models.Model):
    action = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    sanction_outcome = models.ForeignKey(SanctionOutcome, related_name='remediation_action_sanction_outcome', null=True, on_delete=models.SET_NULL,)

    # validate if the sanction outcome is remediation_notice
    def clean_fields(self, exclude=None):
        if self.sanction_outcome.type != 'remediation_notice':
            raise ValidationError({'sanction_outcome': [u'The type of the sanction outcome must be Remediation-Notice when saving a remediation action.']})
        super(RemediationAction, self).clean_fields(exclude)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_RemediationAction'
        verbose_name_plural = 'CM_RemediationActions'

    def __str__(self):
        return '{}'.format(self.action,)


# def update_compliance_doc_filename(instance, filename):
#     return 'wildlifecompliance/compliance/{}/documents/{}'.format(
#         instance.call_email.id, filename)
#
#
# class SanctionOutcomeDocument(Document):
#     sanction_outcome = models.ForeignKey('CallEmail', related_name='documents')
#     _file = models.FileField(upload_to=update_compliance_doc_filename)
#
#     class Meta:
#         app_label = 'wildlifecompliance'
#         verbose_name = 'CM_SanctionOutcomeDocument'
#         verbose_name_plural = 'CM_SanctionOutcomeDocuments'
