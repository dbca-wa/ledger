import datetime

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from ledger.accounts.models import EmailUser, RevisionedMixin
from wildlifecompliance.components.main import get_next_value
from wildlifecompliance.components.main.models import Document, UserAction, CommunicationsLogEntry
from wildlifecompliance.components.offence.models import Offence, Offender, SectionRegulation, AllegedOffence
from wildlifecompliance.components.users.models import RegionDistrict, CompliancePermissionGroup


class SanctionOutcome(models.Model):
    WORKFLOW_SEND_TO_MANAGER = 'send_to_manager'
    WORKFLOW_ENDORSE = 'endorse'
    WORKFLOW_DECLINE = 'decline'
    WORKFLOW_WITHDRAW = 'withdraw'
    WORKFLOW_RETURN_TO_OFFICER = 'return_to_officer'
    WORKFLOW_CLOSE = 'close'

    STATUS_DRAFT = 'draft'
    STATUS_AWAITING_ENDORSEMENT = 'awaiting_endorsement'
    STATUS_AWAITING_PAYMENT = 'awaiting_payment'
    STATUS_AWAITING_REVIEW = 'awaiting_review'
    STATUS_AWAITING_AMENDMENT = 'awaiting_amendment'
    STATUS_DECLINED = 'declined'
    STATUS_WITHDRAWN = 'withdrawn'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = (
        (STATUS_DRAFT, 'Draft'),
        (STATUS_AWAITING_ENDORSEMENT, 'Awaiting Endorsement'),
        (STATUS_AWAITING_PAYMENT, 'Awaiting Payment'),
        (STATUS_AWAITING_REVIEW, 'Awaiting Review'),
        (STATUS_AWAITING_AMENDMENT, 'Awaiting Amendment'),
        (STATUS_DECLINED, 'Declined'),
        (STATUS_WITHDRAWN, 'Withdrawn'),
        (STATUS_CLOSED, 'closed'),
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
    alleged_committed_offences = models.ManyToManyField(AllegedOffence, related_name='sanction_outcome_alleged_committed_offences', through='AllegedCommittedOffence')
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

        if self.alleged_committed_offences.all().count() and not self.offence:
            raise ValidationError('An offence must be selected to save alleged offence(s).')

        # validate if offender is registered under the offence
        if self.offender not in self.offence.offender_set:
            raise ValidationError('Offender must be registered under the selected offence.')

        # validate if alleged_offences are registered under the offence
        # for alleged_offence in self.alleged_committed_offences.all():
        #     if alleged_offence not in self.offence.alleged_offences:
        #         raise ValidationError('Alleged offence must be registered under the selected offence.')

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

        self.__original_status = self.status


    def __str__(self):
        return 'Type : {}, Identifier: {}'.format(self.type, self.identifier)
    
    @property
    def get_related_items_identifier(self):
        #return self.identifier
        return self.lodgement_number

    @property
    def get_related_items_descriptor(self):
        #return '{0}, {1}'.format(self.identifier, self.description)
        return self.identifier

    @property
    def regionDistrictId(self):
        return self.district.id if self.district else self.region.id

    @staticmethod
    def get_compliance_permission_group(regionDistrictId, workflow_type):
        region_district = RegionDistrict.objects.filter(id=regionDistrictId)

        # 2. Determine which permission(s) is going to be apllied
        compliance_content_type = ContentType.objects.get(model="compliancepermissiongroup")
        codename = 'officer'
        if workflow_type == SanctionOutcome.WORKFLOW_SEND_TO_MANAGER:
            codename = 'manager'
            per_district = True
        elif workflow_type == SanctionOutcome.WORKFLOW_DECLINE:
            codename = '---'
            per_district = False
        elif workflow_type == SanctionOutcome.WORKFLOW_ENDORSE:
            codename = 'infringement_notice_coordinator'
            per_district = False
        elif workflow_type == SanctionOutcome.WORKFLOW_RETURN_TO_OFFICER:
            codename = 'officer'
            per_district = True
        elif workflow_type == SanctionOutcome.WORKFLOW_WITHDRAW:
            codename = '---'
            per_district = False
        elif workflow_type == SanctionOutcome.WORKFLOW_CLOSE:
            codename = '---'
            per_district = False
        else:
            # Should not reach here
            # instance.save()
            pass

        permissions = Permission.objects.filter(codename=codename, content_type_id=compliance_content_type.id)

        # 3. Find groups which has the permission(s) determined above in the regionDistrict.
        if per_district:
            groups = CompliancePermissionGroup.objects.filter(region_district__in=region_district, permissions__in=permissions)
        else:
            groups = CompliancePermissionGroup.objects.filter(permissions__in=permissions)

        return groups.first()

    def send_to_manager(self, request):
        if self.issued_on_paper:
            self.status = self.STATUS_AWAITING_ENDORSEMENT
        else:
            self.status = self.STATUS_AWAITING_REVIEW
        new_group = SanctionOutcome.get_compliance_permission_group(self.regionDistrictId, SanctionOutcome.WORKFLOW_SEND_TO_MANAGER)
        self.allocated_group = new_group
        self.log_user_action(SanctionOutcomeUserAction.ACTION_SEND_TO_MANAGER.format(self.lodgement_number), request)
        self.save()

    def endorse(self, request):
        self.status = self.STATUS_AWAITING_PAYMENT
        new_group = SanctionOutcome.get_compliance_permission_group(self.regionDistrictId, SanctionOutcome.WORKFLOW_ENDORSE)
        self.allocated_group = new_group
        current_datetime = datetime.datetime.now()
        self.date_of_issue = current_datetime.date()
        self.time_of_issue = current_datetime.time()
        self.log_user_action(SanctionOutcomeUserAction.ACTION_ENDORSE.format(self.lodgement_number), request)
        self.save()

    def decline(self, request):
        self.status = self.STATUS_DECLINED
        new_group = SanctionOutcome.get_compliance_permission_group(self.regionDistrictId, SanctionOutcome.WORKFLOW_DECLINE)
        self.allocated_group = new_group
        self.log_user_action(SanctionOutcomeUserAction.ACTION_DECLINE.format(self.lodgement_number), request)
        self.save()

    def return_to_officer(self, request):
        self.status = self.STATUS_AWAITING_AMENDMENT
        new_group = SanctionOutcome.get_compliance_permission_group(self.regionDistrictId, SanctionOutcome.WORKFLOW_RETURN_TO_OFFICER)
        self.allocated_group = new_group
        self.log_user_action(SanctionOutcomeUserAction.ACTION_RETURN_TO_OFFICER.format(self.lodgement_number), request)
        self.save()

    def withdraw(self, request):
        self.status = self.STATUS_WITHDRAWN
        new_group = SanctionOutcome.get_compliance_permission_group(self.regionDistrictId, SanctionOutcome.WORKFLOW_WITHDRAW)
        self.allocated_group = new_group
        self.log_user_action(SanctionOutcomeUserAction.ACTION_WITHDRAW.format(self.lodgement_number), request)
        self.save()

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_SanctionOutcome'
        verbose_name_plural = 'CM_SanctionOutcomes'


class AllegedCommittedOffence(RevisionedMixin):
    alleged_offence = models.ForeignKey(AllegedOffence, null=False,)
    sanction_outcome = models.ForeignKey(SanctionOutcome, null=False,)
    included = models.BooleanField(default=True)  # True means sanction_outcome is included in the sanction_outcome
    reason_for_removal = models.TextField(blank=True)
    removed = models.BooleanField(default=False)  # Never make this field False once becomes True. Rather you have to create another record making this field False.
    removed_by = models.ForeignKey(EmailUser, null=True, related_name='alleged_committed_offence_removed_by')

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_AllegedCommittedOffence'
        verbose_name_plural = 'CM_AllegedCommittedOffences'

    # def clean(self):
    #     raise ValidationError('Error test')
    #     if not self.included and not self.removed:
    #         raise ValidationError('Alleged offence: %s is not included, but is going to be removed' % self.alleged_offence)


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
    ACTION_SEND_TO_MANAGER = "Send Sanction Outcome {} to manager"
    ACTION_ENDORSE = "Endorse Sanction Outcome {}"
    ACTION_DECLINE = "Decline Sanction Outcome {}"
    ACTION_RETURN_TO_OFFICER = "Request amendment for Sanction Outcome {}"
    ACTION_WITHDRAW = "Withdraw Sanction Outcome {}"
    # ACTION_EXTEND_DUE_DATE = "Extend Sanction Outcome {} Payment Due Date"
    # ACTION_SEND_TO_DOT = "Send Sanction Outcome {} to Department of Transport"
    # ACTION_SEND_TO_FINES_ENFORCEMENT_UNIT = "Send Sanction Outcome {} to Fined Enforcement Unit"
    # ACTION_ESCALATE_FOR_WITHDRAWAL = "Escalate Sanction Outcome {} for Withdrawal"
    # ACTION_RETURN_TO_INFRINGEMENT_NOTICE_COORDINATOR = "Return Sanction Outcome {} to Infringement Notice Coordinator"
    ACTION_CLOSE = "Close Sanction Outcome {}"
    ACTION_ADD_WEAK_LINK = "Create manual link between Sanction Outcome: {} and {}: {}"
    ACTION_REMOVE_WEAK_LINK = "Remove manual link between Sanction Outcome: {} and {}: {}"

    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, obj, action, user):
        return cls.objects.create(
            sanction_outcome=obj,
            who=user,
            what=str(action)
        )

    sanction_outcome = models.ForeignKey(SanctionOutcome, related_name='action_logs')
