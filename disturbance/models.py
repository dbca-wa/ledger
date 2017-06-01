from __future__ import unicode_literals

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.sites.models import Site
from taggit.managers import TaggableManager
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import EmailUser, Document, RevisionedMixin
from ledger.licence.models import  Licence
from disturbance.fields import CommaSeparatedField


@python_2_unicode_compatible
class Region(models.Model):
    name = models.CharField(max_length=200, blank=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

@python_2_unicode_compatible
class UserAction(models.Model):
    who = models.ForeignKey(EmailUser, null=False, blank=False)
    when = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    what = models.TextField(blank=False)

    def __str__(self):
        return "{what} ({who} at {when})".format(
            what=self.what,
            who=self.who,
            when=self.when
        )

    class Meta:
        abstract = True

class CommunicationsLogEntry(models.Model):
    TYPE_CHOICES = [('email', 'Email'), ('phone', 'Phone Call'), ('main', 'Mail'), ('person', 'In Person')]
    DEFAULT_TYPE = TYPE_CHOICES[0][0]

    to = models.CharField(max_length=200, blank=True, verbose_name="To")
    fromm = models.CharField(max_length=200, blank=True, verbose_name="From")
    cc = models.CharField(max_length=200, blank=True, verbose_name="cc")

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DEFAULT_TYPE)
    reference = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200, blank=True, verbose_name="Subject / Description")
    text = models.TextField(blank=True)
    documents = models.ManyToManyField(Document, blank=True)

    customer = models.ForeignKey(EmailUser, null=True, related_name='customer')
    staff = models.ForeignKey(EmailUser, null=True, related_name='staff')

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

@python_2_unicode_compatible
class Organisation(models.Model):
    organisation = models.ForeignKey(ledger_organisation)
    # TODO: business logic related to delegate changes.
    delegates = models.ManyToManyField(EmailUser, blank=True, through='UserDelegation', related_name='disturbance_organisations')
    pin_one = models.CharField(max_length=50,blank=True)
    pin_two = models.CharField(max_length=50,blank=True)

    def __str__(self):
        return str(self.organisation)

    def validate_pins(self,pin1,pin2):
        return self.pin_one == pin1 and self.pin_two == pin2
    
    def link_user(self,user):
        try:
            UserDelegation.objects.find(organisation=self,user=user)
            raise ValidationError('This user has already been linked to {}'.format(str(self.organisation)))
        except UserDelegation.DoesNotExist:
            UserDelegation.objects.create(organisation=self,user=user)

    @staticmethod
    def existance(abn):
        exists = True
        org = None
        l_org = None
        try:
            try:
                l_org = ledger_organisation.objects.get(abn=abn)
            except ledger_organisation.DoesNotExist:
                exists = False
            if l_org:
                try:
                    org = Organisation.objects.get(organisation=l_org).id
                except Organisation.DoesNotExist:
                    exists = False
            return {'exists': exists, 'id': org}
        except:
            raise

@python_2_unicode_compatible
class OrganisationContact(models.Model):
    organisation = models.ForeignKey(Organisation, related_name='contacts')
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=128, blank=False, verbose_name='Given name(s)')
    last_name = models.CharField(max_length=128, blank=False)
    phone_number = models.CharField(max_length=50, null=True, blank=True,
                                    verbose_name="phone number", help_text='')
    mobile_number = models.CharField(max_length=50, null=True, blank=True,
                                     verbose_name="mobile number", help_text='')
    fax_number = models.CharField(max_length=50, null=True, blank=True,
                                  verbose_name="fax number", help_text='')

    def __str__(self):
        return '{} {}'.format(self.last_name,self.first_name)

class UserDelegation(models.Model):
    organisation = models.ForeignKey(Organisation)
    user = models.ForeignKey(EmailUser)

    class Meta:
        unique_together = (('organisation','user'),)
    
class OrganisationRequest(models.Model):
    STATUS_CHOICES = (
        ('new','New'),
        ('with_assessor','With Assessor'),
        ('approved','Approved'),
        ('declined','Declined')
    )
    name = models.CharField(max_length=128, unique=True)
    abn = models.CharField(max_length=50, null=True, blank=True, verbose_name='ABN')
    requester = models.ForeignKey(EmailUser)
    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True, related_name='org_request_assignee')
    identification = models.FileField(upload_to='organisation/requests/%Y/%m/%d', null=True, blank=True)
    status = models.CharField(max_length=100,choices=STATUS_CHOICES, default="new")
    lodgement_date = models.DateTimeField(auto_now_add=True)

class ProposalType(models.Model):
    schema = JSONField()
    activities = TaggableManager(verbose_name="Activities",help_text="A comma-separated list of activities.") 
    site = models.OneToOneField(Site, default='1') 

class Proposal(RevisionedMixin):

    CUSTOMER_STATUS_CHOICES = (('temp', 'Temporary'), ('draft', 'Draft'), ('under_review', 'Under Review'),
                               ('id_required', 'Identification Required'),
                               ('returns_required', 'Returns Completion Required'),
                               ('amendment_required', 'Amendment Required'),
                               ('id_and_amendment_required', 'Identification/Amendments Required'),
                               ('id_and_returns_required', 'Identification/Returns Required'),
                               ('returns_and_amendment_required', 'Returns/Amendments Required'),
                               ('id_and_returns_and_amendment_required', 'Identification/Returns/Amendments Required'),
                               ('approved', 'Approved'),
                               ('declined', 'Declined'),
                               ('discarded', 'Discarded'),
                               )

    # List of statuses from above that allow a customer to edit an application.
    CUSTOMER_EDITABLE_STATE = ['temp', 'draft', 'amendment_required', 'id_and_amendment_required',
                               'returns_and_amendment_required',
                               'id_and_returns_and_amendment_required']

    # List of statuses from above that allow a customer to view an application (read-only)
    CUSTOMER_VIEWABLE_STATE = ['under_review', 'id_required', 'returns_required', 'approved', 'declined']

    PROCESSING_STATUS_CHOICES = (('temp', 'Temporary'), ('draft', 'Draft'), ('new', 'New'), ('renewal', 'Renewal'),
                                 ('licence_amendment', 'Licence Amendment'), ('ready_for_action', 'Ready for Action'),
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

    APPLICANT_TYPES = (
        (1,'Person'),
        (2,'Organisation')
    )

    data = JSONField(blank=True, null=True)
    documents = models.ManyToManyField(Document)
    hard_copy = models.ForeignKey(Document, blank=True, null=True, related_name='hard_copy')
    
    customer_status = models.CharField('Customer Status', max_length=40, choices=CUSTOMER_STATUS_CHOICES,
                                       default=CUSTOMER_STATUS_CHOICES[0][0])
    applicant_type = models.SmallIntegerField(default=1,choices=APPLICANT_TYPES)
    applicant_user = models.ForeignKey(EmailUser, blank=True, null=True, related_name='disturbance_applications')
    applicant_org = models.ForeignKey(Organisation, blank=True, null=True, related_name='applications')

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


    def __str__(self):
        return self.reference

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

    def log_user_action(self, action, request):
        return ApplicationUserAction.log_action(self, action, request.user)

class ProposalLogEntry(CommunicationsLogEntry):
    proposal = models.ForeignKey(Proposal)

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

class IDRequest(ProposalRequest):
    REASON_CHOICES = (('missing', 'There is currently no Photographic Identification uploaded'),
                      ('expired', 'The current identification has expired'),
                      ('not_recognised',
                       'The current identification is not recognised by the Department of Parks and Wildlife'),
                      ('illegible', 'The current identification image is of poor quality and cannot be made out.'),
                      ('other', 'Other'))
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])


class ComplianceRequest(ProposalRequest):
    REASON_CHOICES = (('outstanding', 'There are currently outstanding returns for the previous licence'),
                      ('other', 'Other'))
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])


class AmendmentRequest(ProposalRequest):
    STATUS_CHOICES = (('requested', 'Requested'), ('amended', 'Amended'))
    REASON_CHOICES = (('insufficient_detail', 'The information provided was insufficient'),
                      ('missing_information', 'There was missing information'),
                      ('other', 'Other'))
    status = models.CharField('Status', max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])

class Assessment(ProposalRequest):
    STATUS_CHOICES = (('awaiting_assessment', 'Awaiting Assessment'), ('assessed', 'Assessed'),
                      ('assessment_expired', 'Assessment Period Expired'))
    assigned_assessor = models.ForeignKey(EmailUser, blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    date_last_reminded = models.DateField(null=True, blank=True)
    requirements = models.ManyToManyField('Requirement', through='AssessmentRequirement')
    comment = models.TextField(blank=True)
    purpose = models.TextField(blank=True)

class ProposalDeclinedDetails(models.Model):
    proposal = models.ForeignKey(Proposal)
    officer = models.ForeignKey(EmailUser, null=False)
    reason = models.TextField(blank=True)

@python_2_unicode_compatible
class Requirement(RevisionedMixin):
    text = models.TextField()
    code = models.CharField(max_length=10, unique=True)
    one_off = models.BooleanField(default=False)
    obsolete = models.BooleanField(default=False)

    def __str__(self):
        return self.code

class AssessmentRequirement(models.Model):
    ACCEPTANCE_STATUS_CHOICES = (('not_specified', 'Not Specified'), ('accepted', 'Accepted'), ('declined', 'Declined'))
    requirement = models.ForeignKey(Requirement)
    assessment = models.ForeignKey(Assessment)
    order = models.IntegerField()
    acceptance_status = models.CharField('Acceptance Status', max_length=20, choices=ACCEPTANCE_STATUS_CHOICES,
                                         default=ACCEPTANCE_STATUS_CHOICES[0][0])

    class Meta:
        unique_together = ('requirement', 'assessment', 'order')

class ProposalRequirement(models.Model):
    requirement = models.ForeignKey(Requirement)
    proposal = models.ForeignKey(Proposal)
    order = models.IntegerField()

    class Meta:
        unique_together = ('requirement', 'proposal', 'order')

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
    # Assessors
    ACTION_SAVE_ASSESSMENT_ = "Save assessment {}"
    ACTION_CONCLUDE_ASSESSMENT_ = "Conclude assessment {}"

    @classmethod
    def log_action(cls, proposal, action, user):
        return cls.objects.create(
            proposal=proposal,
            who=user,
            what=str(action)
        )

    proposal = models.ForeignKey(Proposal)

@receiver(pre_delete, sender=Proposal)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()
