from __future__ import unicode_literals

from django.db import models,transaction
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields.jsonb import JSONField
from django.utils import timezone
from django.contrib.sites.models import Site
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import EmailUser, Document, RevisionedMixin
from ledger.licence.models import  Licence
from disturbance.components.organisations.models import Organisation
from disturbance.components.main.models import CommunicationsLogEntry, Region, UserAction
from disturbance.components.main.utils import get_department_user
from disturbance.components.proposals.email import send_referral_email_notification

class ProposalType(models.Model):
    schema = JSONField()
    activities = TaggableManager(verbose_name="Activities",help_text="A comma-separated list of activities.")
    site = models.OneToOneField(Site, default='1')

    class Meta:
        app_label = 'disturbance'


class TaggedProposalAssessorGroupRegions(TaggedItemBase):
    content_object = models.ForeignKey("ProposalAssessorGroup")

    class Meta:
        app_label = 'disturbance'

class TaggedProposalAssessorGroupActivities(TaggedItemBase):
    content_object = models.ForeignKey("ProposalAssessorGroup")

    class Meta:
        app_label = 'disturbance'

class ProposalAssessorGroup(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(EmailUser,blank=True)
    regions = TaggableManager(verbose_name="Regions",help_text="A comma-separated list of regions.",through=TaggedProposalAssessorGroupRegions,related_name = "+",blank=True)
    activities = TaggableManager(verbose_name="Activities",help_text="A comma-separated list of activities.",through=TaggedProposalAssessorGroupActivities,related_name = "+",blank=True)
    default = models.BooleanField(default=False)

    class Meta:
        app_label = 'disturbance'

    def __str__(self):
        return self.name

    def clean(self):
        try:
            default = ProposalAssessorGroup.objects.get(default=True)
        except ProposalAssessorGroup.DoesNotExist:
            default = None

        if self.pk:
            if int(self.pk) != int(default.id):
                if default and self.default:
                    raise ValidationError('There can only be one default proposal assessor group')
        else:
            if default and self.default:
                raise ValidationError('There can only be one default proposal assessor group')

    @property
    def all_members(self):
        all_members = []
        all_members.extend(self.members.all())
        member_ids = [m.id for m in self.members.all()]
        all_members.extend(EmailUser.objects.filter(is_superuser=True,is_staff=True,is_active=True).exclude(id__in=member_ids))
        return all_members

    class Meta:
        app_label = 'disturbance'

class Proposal(RevisionedMixin):

    CUSTOMER_STATUS_CHOICES = (('temp', 'Temporary'), ('draft', 'Draft'),
                               ('with_assessor', 'Under Review'),
                               ('amendment_required', 'Amendment Required'),
                               ('approved', 'Approved'),
                               ('declined', 'Declined'),
                               ('discarded', 'Discarded'),
                               )

    # List of statuses from above that allow a customer to edit an application.
    CUSTOMER_EDITABLE_STATE = ['temp',
                                'draft',
                                'amendment_required',
                            ]

    # List of statuses from above that allow a customer to view an application (read-only)
    CUSTOMER_VIEWABLE_STATE = ['with_assessor', 'under_review', 'id_required', 'returns_required', 'approved', 'declined']

    PROCESSING_STATUS_CHOICES = (('temp', 'Temporary'), 
                                 ('draft', 'Draft'), 
                                 ('with_assessor', 'With Assessor'),
                                 ('with_referral', 'With Referral'),
                                 ('ready_for_action', 'Ready for Action'),
                                 ('renewal', 'Renewal'),
                                 ('licence_amendment', 'Licence Amendment'), 
                                 ('awaiting_applicant_response', 'Awaiting Applicant Response'),
                                 ('awaiting_assessor_response', 'Awaiting Assessor Response'),
                                 ('awaiting_responses', 'Awaiting Responses'),
                                 ('ready_for_conditions', 'Ready for Conditions'),
                                 ('ready_to_issue', 'Ready to Issue'),
                                 ('issued', 'Issued'),
                                 ('declined', 'Declined'),
                                 ('discarded', 'Discarded'),
                                 )

    ID_CHECK_STATUS_CHOICES = (('not_checked', 'Not Checked'), ('awaiting_update', 'Awaiting Update'),
                               ('updated', 'Updated'), ('accepted', 'Accepted'))

    COMPLIANCE_CHECK_STATUS_CHOICES = (
        ('not_checked', 'Not Checked'), ('awaiting_returns', 'Awaiting Returns'), ('completed', 'Completed'),
        ('accepted', 'Accepted'))

    CHARACTER_CHECK_STATUS_CHOICES = (
        ('not_checked', 'Not Checked'), ('accepted', 'Accepted'))

    REVIEW_STATUS_CHOICES = (
        ('not_reviewed', 'Not Reviewed'), ('awaiting_amendments', 'Awaiting Amendments'), ('amended', 'Amended'),
        ('accepted', 'Accepted'))

    data = JSONField(blank=True, null=True)
    assessor_data = JSONField(blank=True, null=True)
    schema = JSONField(blank=False, null=False)
    documents = models.ManyToManyField(Document)
    hard_copy = models.ForeignKey(Document, blank=True, null=True, related_name='hard_copy')

    customer_status = models.CharField('Customer Status', max_length=40, choices=CUSTOMER_STATUS_CHOICES,
                                       default=CUSTOMER_STATUS_CHOICES[0][0])
    applicant = models.ForeignKey(Organisation, blank=True, null=True, related_name='proposals')

    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    lodgement_sequence = models.IntegerField(blank=True, default=0)
    lodgement_date = models.DateField(blank=True, null=True)

    proxy_applicant = models.ForeignKey(EmailUser, blank=True, null=True, related_name='disturbance_proxy')
    submitter = models.ForeignKey(EmailUser, blank=True, null=True, related_name='disturbance_proposals')

    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True, related_name='assignee')
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[0][0])
    id_check_status = models.CharField('Identification Check Status', max_length=30, choices=ID_CHECK_STATUS_CHOICES,
                                       default=ID_CHECK_STATUS_CHOICES[0][0])
    compliance_check_status = models.CharField('Return Check Status', max_length=30, choices=COMPLIANCE_CHECK_STATUS_CHOICES,
                                            default=COMPLIANCE_CHECK_STATUS_CHOICES[0][0])
    character_check_status = models.CharField('Character Check Status', max_length=30,
                                              choices=CHARACTER_CHECK_STATUS_CHOICES,
                                              default=CHARACTER_CHECK_STATUS_CHOICES[0][0])
    review_status = models.CharField('Review Status', max_length=30, choices=REVIEW_STATUS_CHOICES,
                                     default=REVIEW_STATUS_CHOICES[0][0])

    requirements = models.ManyToManyField('Requirement', through='ProposalRequirement')


    previous_application = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    # Special Fields
    activity = models.CharField(max_length=255,null=True,blank=True)
    region = models.CharField(max_length=255,null=True,blank=True)
    title = models.CharField(max_length=255,null=True,blank=True)

    class Meta:
        app_label = 'disturbance'

    def __str__(self):
        return str(self.id)

    @property
    def reference(self):
        return '{}-{}'.format(self.lodgement_number, self.lodgement_sequence)

    @property
    def is_assigned(self):
        return self.assigned_officer is not None

    @property
    def is_temporary(self):
        return self.customer_status == 'temp' and self.processing_status == 'temp'

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
        1 - It is a draft
        2- or if the application has been pushed back to the user
        """
        return self.customer_status == 'draft' or self.processing_status == 'awaiting_applicant_response'

    @property
    def is_deletable(self):
        """
        An application can be deleted only if it is a draft and it hasn't been lodged yet
        :return:
        """
        return self.customer_status == 'draft' and not self.lodgement_number

    @property
    def latest_referrals(self):
        return self.referrals.all()[:2]

    def can_assess(self,user):
        exists = False
        default_group = ProposalAssessorGroup.objects.get(default=True)
        if default_group in user.proposalassessorgroup_set.all():
            exists = True
 
        return exists

    def log_user_action(self, action, request):
        return ProposalUserAction.log_action(self, action, request.user)

    def submit(self,request):
        with transaction.atomic():
            if self.can_user_edit:
                self.processing_status = 'with_assessor'
                self.customer_status = 'with_assessor'
                self.submitter = request.user
                self.lodgement_date = timezone.now().strftime('%Y-%m-%d') 
                self.save()
                # Create a log entry for the proposal
                self.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(self.id),request)
                # Create a log entry for the organisation
                self.applicant.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(self.id),request)
            else:
                raise ValidationError('You can\'t edit this proposal at this moment')

    def send_referral(self,request,referral_email):
        with transaction.atomic():
            try:
                self.processing_status = 'with_referral'
                self.save()
                referral = None
                # Validate if it is a deparment user
                department_user = get_department_user(referral_email)
                if not department_user:
                    raise ValidationError('The user you want to send the referral to is not a member of the department')
                # Check if the user is in ledger or create
                user,created = EmailUser.objects.get_or_create(email=department_user['email'])
                try:
                    Referral.objects.get(referral=user,proposal=self)
                    raise ValidationError('A referral has already been sent to this user')
                except Referral.DoesNotExist:
                    # Create Referral
                    referral = Referral.objects.create(
                        proposal = self,
                        referral=user,
                        sent_by=request.user 
                    )
                # Create a log entry for the proposal
                self.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.id,'{}({})'.format(department_user['name'],department_user['email'])),request)
                # Create a log entry for the organisation
                self.applicant.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.id,'{}({})'.format(department_user['name'],department_user['email'])),request)
                # send email
                send_referral_email_notification(referral,request)
            except:
                raise

class ProposalLogEntry(CommunicationsLogEntry):
    proposal = models.ForeignKey(Proposal, related_name='comms_logs')

    class Meta:
        app_label = 'disturbance'

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.proposal.reference
        super(ProposalLogEntry, self).save(**kwargs)

class ProposalRequest(models.Model):
    proposal = models.ForeignKey(Proposal)
    subject = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    officer = models.ForeignKey(EmailUser, null=True)

    class Meta:
        app_label = 'disturbance'

class IDRequest(ProposalRequest):
    REASON_CHOICES = (('missing', 'There is currently no Photographic Identification uploaded'),
                      ('expired', 'The current identification has expired'),
                      ('not_recognised',
                       'The current identification is not recognised by the Department of Parks and Wildlife'),
                      ('illegible', 'The current identification image is of poor quality and cannot be made out.'),
                      ('other', 'Other'))
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])

    class Meta:
        app_label = 'disturbance'


class ComplianceRequest(ProposalRequest):
    REASON_CHOICES = (('outstanding', 'There are currently outstanding returns for the previous licence'),
                      ('other', 'Other'))
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])

    class Meta:
        app_label = 'disturbance'


class AmendmentRequest(ProposalRequest):
    STATUS_CHOICES = (('requested', 'Requested'), ('amended', 'Amended'))
    REASON_CHOICES = (('insufficient_detail', 'The information provided was insufficient'),
                      ('missing_information', 'There was missing information'),
                      ('other', 'Other'))
    status = models.CharField('Status', max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])

    class Meta:
        app_label = 'disturbance'

class Assessment(ProposalRequest):
    STATUS_CHOICES = (('awaiting_assessment', 'Awaiting Assessment'), ('assessed', 'Assessed'),
                      ('assessment_expired', 'Assessment Period Expired'))
    assigned_assessor = models.ForeignKey(EmailUser, blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    date_last_reminded = models.DateField(null=True, blank=True)
    requirements = models.ManyToManyField('Requirement', through='AssessmentRequirement')
    comment = models.TextField(blank=True)
    purpose = models.TextField(blank=True)

    class Meta:
        app_label = 'disturbance'

class ProposalDeclinedDetails(models.Model):
    proposal = models.ForeignKey(Proposal)
    officer = models.ForeignKey(EmailUser, null=False)
    reason = models.TextField(blank=True)

    class Meta:
        app_label = 'disturbance'

@python_2_unicode_compatible
class Requirement(RevisionedMixin):
    text = models.TextField()
    code = models.CharField(max_length=10, unique=True)
    one_off = models.BooleanField(default=False)
    obsolete = models.BooleanField(default=False)

    def __str__(self):
        return self.code

    class Meta:
        app_label = 'disturbance'

class AssessmentRequirement(models.Model):
    ACCEPTANCE_STATUS_CHOICES = (('not_specified', 'Not Specified'), ('accepted', 'Accepted'), ('declined', 'Declined'))
    requirement = models.ForeignKey(Requirement)
    assessment = models.ForeignKey(Assessment)
    order = models.IntegerField()
    acceptance_status = models.CharField('Acceptance Status', max_length=20, choices=ACCEPTANCE_STATUS_CHOICES,
                                         default=ACCEPTANCE_STATUS_CHOICES[0][0])

    class Meta:
        unique_together = ('requirement', 'assessment', 'order')
        app_label = 'disturbance'

class ProposalRequirement(models.Model):
    requirement = models.ForeignKey(Requirement)
    proposal = models.ForeignKey(Proposal)
    order = models.IntegerField()

    class Meta:
        unique_together = ('requirement', 'proposal', 'order')
        app_label = 'disturbance'

@python_2_unicode_compatible
class DisturbanceLicence(Licence):
    MONTH_FREQUENCY_CHOICES = [(-1, 'One off'), (1, 'Monthly'), (3, 'Quarterly'), (6, 'Twice-Yearly'), (12, 'Yearly')]
    DEFAULT_FREQUENCY = MONTH_FREQUENCY_CHOICES[0][0]

    proposal = models.ForeignKey(Proposal, on_delete=models.PROTECT, related_name='licences')
    purpose = models.TextField(blank=True)
    additional_information = models.TextField(blank=True)
    licence_document = models.ForeignKey(Document, blank=True, null=True, related_name='licence_document')
    cover_letter_document = models.ForeignKey(Document, blank=True, null=True, related_name='cover_letter_document')
    compliance_frequency = models.IntegerField(choices=MONTH_FREQUENCY_CHOICES, default=DEFAULT_FREQUENCY)
    replaced_by = models.ForeignKey('self', blank=True, null=True)
    regions = models.ManyToManyField(Region, blank=False)
    renewal_sent = models.BooleanField(default=False)
    extracted_fields = JSONField(blank=True, null=True)

    class Meta:
        app_label = 'disturbance'

    def __str__(self):
        return self.reference

    @property
    def reference(self):
        return '{}-{}'.format(self.licence_number, self.licence_sequence)

    @property
    def is_issued(self):
        return self.licence_number is not None and len(self.licence_number) > 0

class ProposalUserAction(UserAction):
    ACTION_CREATE_CUSTOMER_ = "Create customer {}"
    ACTION_CREATE_PROFILE_ = "Create profile {}"
    ACTION_LODGE_APPLICATION = "Lodge proposal {}"
    ACTION_ASSIGN_TO_ = "Assign to {}"
    ACTION_UNASSIGN = "Unassign"
    ACTION_ACCEPT_ID = "Accept ID"
    ACTION_RESET_ID = "Reset ID"
    ACTION_ID_REQUEST_UPDATE = 'Request ID update'
    ACTION_ACCEPT_CHARACTER = 'Accept character'
    ACTION_RESET_CHARACTER = "Reset character"
    ACTION_ACCEPT_REVIEW = 'Accept review'
    ACTION_RESET_REVIEW = "Reset review"
    ACTION_ID_REQUEST_AMENDMENTS = "Request amendments"
    ACTION_SEND_FOR_ASSESSMENT_TO_ = "Send for assessment to {}"
    ACTION_SEND_ASSESSMENT_REMINDER_TO_ = "Send assessment reminder to {}"
    ACTION_ASSESSMENT_ASSIGN_TO_ = "Assign Assessment to {}"
    ACTION_ASSESSMENT_UNASSIGN = "Unassign Assessment"
    ACTION_DECLINE_APPLICATION = "Decline proposal"
    ACTION_ENTER_CONDITIONS = "Enter requirement"
    ACTION_CREATE_CONDITION_ = "Create requirement {}"
    ACTION_ISSUE_LICENCE_ = "Issue Licence {}"
    ACTION_DISCARD_APPLICATION = "Discard proposal {}"
    ACTION_SEND_REFERRAL_TO = "Send referral {} for proposal {} to {}"
    ACTION_RESEND_REFERRAL_TO = "Resend referral {} for proposal {} to {}"
    # Assessors
    ACTION_SAVE_ASSESSMENT_ = "Save assessment {}"
    ACTION_CONCLUDE_ASSESSMENT_ = "Conclude assessment {}"

    class Meta:
        app_label = 'disturbance'

    @classmethod
    def log_action(cls, proposal, action, user):
        return cls.objects.create(
            proposal=proposal,
            who=user,
            what=str(action)
        )

    proposal = models.ForeignKey(Proposal, related_name='action_logs')


class Referral(models.Model):
    SENT_CHOICES = (
        (1,'Sent From Assessor'),
        (2,'Sent From Referral')
    )
    PROCESSING_STATUS_CHOICES = (
                                 ('with_referral', 'Awaiting'),
                                 ('recalled', 'Recalled'),
                                 ('completed', 'Completed'),
                                 )
    lodged_on = models.DateTimeField(auto_now_add=True)
    proposal = models.ForeignKey(Proposal,related_name='referrals')
    sent_by = models.ForeignKey(EmailUser,related_name='disturbance_assessor_referrals')
    referral = models.ForeignKey(EmailUser,null=True,blank=True,related_name='disturbance_referalls')
    linked = models.BooleanField(default=False)
    sent_from = models.SmallIntegerField(choices=SENT_CHOICES,default=SENT_CHOICES[0][0])
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[0][0]) 

    class Meta:
        app_label = 'disturbance'
        ordering = ('-lodged_on',)

    def __str__(self):
        return 'Proposal {} - Referral {}'.format(self.proposal.id,self.id)
    
    # Methods

    def send_email(self,request):
        pass

    def recall(self,request):
        self.processing_status = 'recalled'
        # TODO create action for recalling
        #self.save()

    def resend(self,request):
        self.send_email()

    # Properties
    @property
    def region(self):
        return self.proposal.region

    @property
    def activity(self):
        return self.proposal.activity

    @property
    def title(self):
        return self.proposal.title

    @property
    def applicant(self):
        return self.proposal.applicant.name

    @property
    def can_be_processed(self):
        return self.processing_status == 'with_referral'

@receiver(pre_delete, sender=Proposal)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()
