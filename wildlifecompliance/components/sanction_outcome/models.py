from django.core.exceptions import ValidationError
from django.db import models

from ledger.accounts.models import EmailUser
from wildlifecompliance.components.main import get_next_value
from wildlifecompliance.components.main.models import Document, UserAction, CommunicationsLogEntry
from wildlifecompliance.components.offence.models import Offence, Offender, SectionRegulation
from wildlifecompliance.components.users.models import RegionDistrict, CompliancePermissionGroup


class SanctionOutcome(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_WITH_MANAGER = 'with_manager'
    STATUS_WITH_OFFICER = 'with_officer'
    STATUS_CLOSED = 'closed'
    STATUS_WITHDRAWN = 'withdrawn'
    STATUS_CLOSED_ISSUED = 'closed_issued'
    STATUS_CLOSED_WITHDRAWN = 'closed_withdrawn'
    STATUS_AWAITING_PAYMENT = 'awaiting_payment'
    STATUS_AWAITING_PAYMENT_EXTENDED = 'awaiting_payment_extended'
    STATUS_ISSUED = 'issued'
    STATUS_OVERDUE = 'overdue'

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_WITH_MANAGER, 'With Mnager'),
        (STATUS_WITH_OFFICER, 'With Officer'),
        (STATUS_CLOSED, 'Closed'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
        (STATUS_CLOSED_ISSUED, 'Closed (Issued)'),
        (STATUS_CLOSED_WITHDRAWN, 'Closed (Withdrawn)'),
        (STATUS_AWAITING_PAYMENT, 'Awaiting Payment'),
        (STATUS_AWAITING_PAYMENT_EXTENDED, 'Awaiting Payment Extended)'),
        (STATUS_ISSUED, 'Issued'),
        (STATUS_OVERDUE, 'Overdue'),
    )

    TYPE_INFRINGEMENT_NOTICE = 'infringement_notice'
    TYPE_CAUTION_NOTICE = 'caution_notice'
    TYPE_LETTER_OF_ADVICE = 'letter_of_advice'
    TYPE_REMEDIATION_NOTICE = 'remediation_notice'

    TYPE_CHOICES = (
        (TYPE_INFRINGEMENT_NOTICE, 'Infringement Notice'),
        (TYPE_CAUTION_NOTICE, 'Caution Notice'),
        (TYPE_LETTER_OF_ADVICE, 'Letter of Advice'),
        (TYPE_REMEDIATION_NOTICE, 'Remediation Notice'),
    )

    __original_status = STATUS_DRAFT

    type = models.CharField(max_length=30, choices=TYPE_CHOICES, blank=True,)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default=__original_status,)

    region = models.ForeignKey(RegionDistrict, related_name='sanction_outcome_region', null=True,)
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
        if self.type == self.TYPE_LETTER_OF_ADVICE:
            self.issued_on_paper = True

        super(SanctionOutcome, self).clean()

    @property
    def prefix_lodgement_nubmer(self):
        prefix_lodgement = ''
        if self.type == self.TYPE_INFRINGEMENT_NOTICE:
            prefix_lodgement = 'IF'
        elif self.type == self.TYPE_LETTER_OF_ADVICE:
            prefix_lodgement = 'LA'
        elif self.type == self.TYPE_CAUTION_NOTICE:
            prefix_lodgement = 'CN'
        elif self.type == self.TYPE_REMEDIATION_NOTICE:
            prefix_lodgement = 'RN'

        return prefix_lodgement

    def delete(self):
        if self.lodgement_number:
            raise ValidationError('Sanction outcome saved in the database with the logement number cannot be deleted.')

        super(SanctionOutcome, self).delete()

    def log_user_action(self, action, request):
        return SanctionOutcomeUserAction.log_action(self, action, request.user)

    def save(self, *args, **kwargs):
        super(SanctionOutcome, self).save(*args, **kwargs)
        if not self.lodgement_number:
            self.lodgement_number = self.prefix_lodgement_nubmer + '{0:06d}'.format(self.pk)
            self.save()

        if self.__original_status != self.status:
            # status changed
            if self.status == self.STATUS_DRAFT:
                pass

        # TODO: add date_of_issue and time_of_issue

        self.__original_status = self.status


    def __str__(self):
        return 'Type : {}, Identifier: {}'.format(self.type, self.identifier)

    # def send_to_manager(self, request):
    #     self.status = self.STATUS_WITH_MANAGER
    #     self.log_user_action(SanctionOutcomeUserAction.ACTION_SEND_TO_MANAGER.format(self.number), request)
    #     self.save()

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_SanctionOutcome'
        verbose_name_plural = 'CM_SanctionOutcomes'


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
    _file = models.FileField(max_length=255, upload_to=update_compliance_doc_filename)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_SanctionOutcomeDocument'
        verbose_name_plural = 'CM_SanctionOutcomeDocuments'


class SanctionOutcomeCommsLogDocument(Document):
    log_entry = models.ForeignKey('SanctionOutcomeCommsLogEntry', related_name='documents')
    _file = models.FileField(max_length=255)

    class Meta:
        app_label = 'wildlifecompliance'


class SanctionOutcomeCommsLogEntry(CommunicationsLogEntry):
    sanction_outcome = models.ForeignKey(SanctionOutcome, related_name='comms_logs')

    class Meta:
        app_label = 'wildlifecompliance'


class SanctionOutcomeUserAction(UserAction):
    ACTION_SAVE_SANCTION_OUTCOME = "Save Sanction Outcome {}"
    ACTION_SEND_TO_MANAGER = "Send Sanction Outcome {} to manager"
    ACTION_ENDORSE = "Endorse Sanction Outcome {}"
    ACTION_DECLINE = "Decline Sanction Outcome {}"
    ACTION_RETURN_TO_OFFICER = "Return Sanction Outcome {} to officer"
    ACTION_ISSUE = "Issue Sanction Outcome {}"
    ACTION_WITHDRAW = "Withdraw Sanction Outcome {}"
    ACTION_EXTEND_DUE_DATE = "Extend Sanction Outcome {} Payment Due Date"
    ACTION_SEND_TO_DOT = "Send Sanction Outcome {} to Department of Transport"
    ACTION_SEND_TO_FINES_ENFORCEMENT_UNIT = "Send Sanction Outcome {} to Fined Enforcement Unit"
    ACTION_ESCALATE_FOR_WITHDRAWAL = "Escalate Sanction Outcome {} for Withdrawal"
    ACTION_RETURN_TO_INFRINGEMENT_NOTICE_COORDINATOR = "Return Sanction Outcome {} to Infringement Notice Coordinator"
    ACTION_CLOSE = "Close Sanction Outcome {}"

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

    sanction_outcome = models.ForeignKey(SanctionOutcome, related_name='action_logs')
