from django.core.exceptions import ValidationError
from django.db import models

from ledger.accounts.models import EmailUser
from wildlifecompliance.components.main import get_next_value
from wildlifecompliance.components.main.models import Document
from wildlifecompliance.components.offence.models import Offence, Offender, SectionRegulation
from wildlifecompliance.components.users.models import RegionDistrict, CompliancePermissionGroup


class SanctionOutcome(models.Model):
    TYPE_CHOICES = (
        ('infringement_notice', 'Infringement Notice'),
        ('caution_notice', 'Caution Notice'),
        ('letter_of_advice', 'Letter of Advice'),
        ('remediation_notice', 'Remediation Notice'),
    )

    type = models.CharField(max_length=30, choices=TYPE_CHOICES, blank=True,)

    # We may not need this field
    region = models.ForeignKey(RegionDistrict, related_name='sanction_outcome_region', null=True,)
    # We may not need this field
    district = models.ForeignKey(RegionDistrict, related_name='sanction_outcome_district', null=True,)

    identifier = models.CharField(max_length=50, blank=True,)
    lodgement_number = models.CharField(max_length=50, blank=True,)
    offence = models.ForeignKey(Offence, related_name='sanction_outcome_offence', null=True, on_delete=models.SET_NULL,)
    offender = models.ForeignKey(Offender, related_name='sanction_outcome_offender', null=True, on_delete=models.SET_NULL,)
    alleged_offences = models.ManyToManyField(SectionRegulation, blank=True, related_name='sanction_outcome_alleged_offences')
    issued_on_paper = models.BooleanField(default=False) # This is always true when type is letter_of_advice
    paper_id = models.CharField(max_length=50, blank=True,)
    description = models.TextField(blank=True)

    # We may not need this field
    assigned_to = models.ForeignKey(EmailUser, related_name='sanction_outcome_assigned_to', null=True)

    allocated_group = models.ForeignKey(CompliancePermissionGroup, related_name='sanction_outcome_allocated_group', null=True)

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

    def save(self, *args, **kwargs):
        if not self.id:
            if self.type:
                # User is going to save new sanction outcome.  We want to generate next lodgement_number.
                temp1 = get_next_value('infringement_notice')
                temp2 = get_next_value('letter_of_advice')
            else:
                # self is very new sanction outcome object being created only for immediate-file-upload purpose.
                # User has not clicked on the "Send to Manager" button yet.
                # Therefore this object may be deleted from the database
                pass
        else:
            if not self.number:
                # self exists in the database already because it was created just for immediate-file-upload purpose.
                # However it is the first time to save this object by the click on the 'Send to Manager' button.
                temp1 = get_next_value('infringement_notice')
                temp2 = get_next_value('letter_of_advice')
            else:
                # self exists in the database already, and it has a number and id.
                pass
        super(SanctionOutcome, self).save(*args, **kwargs)
    #
    def delete(self):

    #     # TODO: Once created, must not be deleted as long as self.number has some value.

        super(SanctionOutcome, self).delete()

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


def update_compliance_doc_filename(instance, filename):
    return 'wildlifecompliance/sanction_outcome/{}/documents/{}'.format(
        instance.sanction_outcome.id, filename)


class SanctionOutcomeDocument(Document):
    sanction_outcome = models.ForeignKey(SanctionOutcome, related_name='documents')
    _file = models.FileField(upload_to=update_compliance_doc_filename)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_SanctionOutcomeDocument'
        verbose_name_plural = 'CM_SanctionOutcomeDocuments'
