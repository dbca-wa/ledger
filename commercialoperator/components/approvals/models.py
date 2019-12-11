from __future__ import unicode_literals

import json
import datetime
from django.db import models,transaction
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields.jsonb import JSONField
from django.utils import timezone
from django.contrib.sites.models import Site
from django.conf import settings
from django.db.models import Q
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.licence.models import  Licence
from commercialoperator import exceptions
from commercialoperator.components.organisations.models import Organisation
from commercialoperator.components.proposals.models import Proposal, ProposalUserAction
from commercialoperator.components.main.models import CommunicationsLogEntry, UserAction, Document, ApplicationType
from commercialoperator.components.approvals.email import (
    send_approval_expire_email_notification,
    send_approval_cancel_email_notification,
    send_approval_suspend_email_notification,
    send_approval_reinstate_email_notification,
    send_approval_surrender_email_notification
)
from commercialoperator.utils import search_keys, search_multiple_keys
from commercialoperator.helpers import is_customer
#from commercialoperator.components.approvals.email import send_referral_email_notification


def update_approval_doc_filename(instance, filename):
    return '{}/proposals/{}/approvals/{}'.format(settings.MEDIA_APP_DIR, instance.approval.current_proposal.id,filename)

def update_approval_comms_log_filename(instance, filename):
    return '{}/proposals/{}/approvals/communications/{}'.format(settings.MEDIA_APP_DIR, instance.log_entry.approval.current_proposal.id,filename)


class ApprovalDocument(Document):
    approval = models.ForeignKey('Approval',related_name='documents')
    _file = models.FileField(upload_to=update_approval_doc_filename)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted

    def delete(self):
        if self.can_delete:
            return super(ApprovalDocument, self).delete()
        logger.info('Cannot delete existing document object after Application has been submitted (including document submitted before Application pushback to status Draft): {}'.format(self.name))


    class Meta:
        app_label = 'commercialoperator'

#class Approval(models.Model):
class Approval(RevisionedMixin):
    STATUS_CHOICES = (
        ('current','Current'),
        ('expired','Expired'),
        ('cancelled','Cancelled'),
        ('surrendered','Surrendered'),
        ('suspended','Suspended'),
        ('extended','extended'),
    )
    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    status = models.CharField(max_length=40, choices=STATUS_CHOICES,
                                       default=STATUS_CHOICES[0][0])
    licence_document = models.ForeignKey(ApprovalDocument, blank=True, null=True, related_name='licence_document')
    cover_letter_document = models.ForeignKey(ApprovalDocument, blank=True, null=True, related_name='cover_letter_document')
    replaced_by = models.ForeignKey('self', blank=True, null=True)
    #current_proposal = models.ForeignKey(Proposal,related_name = '+')
    current_proposal = models.ForeignKey(Proposal,related_name='approvals', null=True)
#    activity = models.CharField(max_length=255)
#    region = models.CharField(max_length=255)
#    tenure = models.CharField(max_length=255,null=True)
#    title = models.CharField(max_length=255)
    renewal_document = models.ForeignKey(ApprovalDocument, blank=True, null=True, related_name='renewal_document')
    renewal_sent = models.BooleanField(default=False)
    issue_date = models.DateTimeField()
    original_issue_date = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    expiry_date = models.DateField()
    surrender_details = JSONField(blank=True,null=True)
    suspension_details = JSONField(blank=True,null=True)
    submitter = models.ForeignKey(EmailUser, on_delete=models.PROTECT, blank=True, null=True, related_name='commercialoperator_approvals')
    org_applicant = models.ForeignKey(Organisation,on_delete=models.PROTECT, blank=True, null=True, related_name='org_approvals')
    proxy_applicant = models.ForeignKey(EmailUser,on_delete=models.PROTECT, blank=True, null=True, related_name='proxy_approvals')
    extracted_fields = JSONField(blank=True, null=True)
    cancellation_details = models.TextField(blank=True)
    extend_details = models.TextField(blank=True)
    cancellation_date = models.DateField(blank=True, null=True)
    set_to_cancel = models.BooleanField(default=False)
    set_to_suspend = models.BooleanField(default=False)
    set_to_surrender = models.BooleanField(default=False)

    #application_type = models.ForeignKey(ApplicationType, null=True, blank=True)
    renewal_count = models.PositiveSmallIntegerField('Number of times an Approval has been renewed', default=0)
    migrated=models.BooleanField(default=False)

    class Meta:
        app_label = 'commercialoperator'
        unique_together= ('lodgement_number', 'issue_date')

    @property
    def bpay_allowed(self):
        if self.org_applicant:
            return self.org_applicant.bpay_allowed
        return False

    @property
    def monthly_invoicing_allowed(self):
        if self.org_applicant:
            return self.org_applicant.monthly_invoicing_allowed
        return False

    @property
    def monthly_invoicing_period(self):
        if self.org_applicant:
            return self.org_applicant.monthly_invoicing_period
        return None

    @property
    def monthly_payment_due_period(self):
        if self.org_applicant:
            return self.org_applicant.monthly_payment_due_period
        return None

    @property
    def applicant(self):
        if self.org_applicant:
            return self.org_applicant.organisation.name
        elif self.proxy_applicant:
            return "{} {}".format(
                self.proxy_applicant.first_name,
                self.proxy_applicant.last_name)
        else:
            #return None
            try:
                return "{} {}".format(
                    self.submitter.first_name,
                    self.submitter.last_name)
            except:
                return "Applicant Not Set"

    @property
    def linked_applications(self):
        ids = Proposal.objects.filter(approval__lodgement_number=self.lodgement_number).values_list('id', flat=True)
        all_linked_ids = Proposal.objects.filter(Q(previous_application__in=ids) | Q(id__in=ids)).values_list('lodgement_number', flat=True)
        return all_linked_ids

    @property
    def applicant_type(self):
        if self.org_applicant:
            return "org_applicant"
        elif self.proxy_applicant:
            return "proxy_applicant"
        else:
            #return None
            return "submitter"

    @property
    def is_org_applicant(self):
        return True if self.org_applicant else False

    @property
    def applicant_id(self):
        if self.org_applicant:
            #return self.org_applicant.organisation.id
            return self.org_applicant.id
        elif self.proxy_applicant:
            return self.proxy_applicant.id
        else:
            #return None
            return self.submitter.id

    @property
    def region(self):
        return self.current_proposal.region.name

    @property
    def district(self):
        return self.current_proposal.district.name

    @property
    def tenure(self):
        return self.current_proposal.tenure.name

    @property
    def activity(self):
        return self.current_proposal.activity

    @property
    def title(self):
        return self.current_proposal.title

    @property
    def next_id(self):
        #ids = map(int,[(i.lodgement_number.split('A')[1]) for i in Approval.objects.all()])
        ids = map(int,[i.split('L')[1] for i in Approval.objects.all().values_list('lodgement_number', flat=True) if i])
        return max(ids) + 1 if ids else 1

    def save(self, *args, **kwargs):
        if self.lodgement_number in ['', None]:
            self.lodgement_number = 'L{0:06d}'.format(self.next_id)
            #self.save()
        super(Approval, self).save(*args,**kwargs)

    def __str__(self):
        return self.lodgement_number

    @property
    def reference(self):
        return 'L{}'.format(self.id)

    @property
    def can_reissue(self):
        return self.status == 'current' or self.status == 'suspended'

    @property
    def can_reinstate(self):
        return (self.status == 'cancelled' or self.status == 'suspended' or self.status == 'surrendered') and self.can_action

    @property
    def allowed_assessors(self):
        return self.current_proposal.allowed_assessors


    def is_assessor(self,user):
        return self.current_proposal.is_assessor(user)


    def is_approver(self,user):
        return self.current_proposal.is_approver(user)


    @property
    def is_issued(self):
        return self.licence_number is not None and len(self.licence_number) > 0

    @property
    def can_action(self):
        if not (self.set_to_cancel or self.set_to_suspend or self.set_to_surrender):
                return True
        else:
            return False



    @property
    def can_extend(self):
        if self.current_proposal.application_type.name == 'E Class':
            return self.current_proposal.application_type.max_renewals > self.renewal_count
        return False


    @property
    def can_renew(self):
        try:
#            if self.current_proposal.application_type.name == 'E Class':
#                #return (self.current_proposal.application_type.max_renewals is not None and self.current_proposal.application_type.max_renewals > self.renewal_count)
#                return self.current_proposal.application_type.max_renewals > self.renewal_count
#                #pass
#            else:
            renew_conditions = {
                'previous_application': self.current_proposal,
                'proposal_type': 'renewal'
            }
            proposal=Proposal.objects.get(**renew_conditions)
            if proposal:
                return False
        except Proposal.DoesNotExist:
            return True

    @property
    def can_amend(self):
        try:
            amend_conditions = {
                    'previous_application': self.current_proposal,
                    'proposal_type': 'amendment'
                    }
            proposal=Proposal.objects.get(**amend_conditions)
            if proposal:
                return False
        except Proposal.DoesNotExist:
            if self.can_renew:
                return True
            else:
                return False


    def generate_doc(self, user, preview=False):
        from commercialoperator.components.approvals.pdf import create_approval_doc, create_approval_pdf_bytes
        copied_to_permit = self.copiedToPermit_fields(self.current_proposal) #Get data related to isCopiedToPermit tag

        if preview:
            return create_approval_pdf_bytes(self,self.current_proposal, copied_to_permit, user)

        self.licence_document = create_approval_doc(self,self.current_proposal, copied_to_permit, user)
        self.save(version_comment='Created Approval PDF: {}'.format(self.licence_document.name))
        self.current_proposal.save(version_comment='Created Approval PDF: {}'.format(self.licence_document.name))

#    def generate_preview_doc(self, user):
#        from commercialoperator.components.approvals.pdf import create_approval_pdf_bytes
#        copied_to_permit = self.copiedToPermit_fields(self.current_proposal) #Get data related to isCopiedToPermit tag

    def generate_renewal_doc(self):
        from commercialoperator.components.approvals.pdf import create_renewal_doc
        self.renewal_document = create_renewal_doc(self,self.current_proposal)
        self.save(version_comment='Created Approval PDF: {}'.format(self.renewal_document.name))
        self.current_proposal.save(version_comment='Created Approval PDF: {}'.format(self.renewal_document.name))

    def copiedToPermit_fields(self, proposal):
        p=proposal
        copied_data = []
        search_assessor_data = []
        search_schema = search_multiple_keys(p.schema, primary_search='isCopiedToPermit', search_list=['label', 'name'])
        if p.assessor_data:
            search_assessor_data=search_keys(p.assessor_data, search_list=['assessor', 'name'])
        if search_schema:
            for c in search_schema:
                try:
                    if search_assessor_data:
                        for d in search_assessor_data:
                            if c['name'] == d['name']:
                                if d['assessor']:
                                    #copied_data.append({c['label'], d['assessor']})
                                    copied_data.append({c['label']:d['assessor']})
                except:
                    raise
        return copied_data


    def log_user_action(self, action, request):
       return ApprovalUserAction.log_action(self, action, request.user)


    def expire_approval(self,user):
        with transaction.atomic():
            try:
                today = timezone.localtime(timezone.now()).date()
                if self.status == 'current' and self.expiry_date < today:
                    self.status = 'expired'
                    self.save()
                    send_approval_expire_email_notification(self)
                    proposal = self.current_proposal
                    ApprovalUserAction.log_action(self,ApprovalUserAction.ACTION_EXPIRE_APPROVAL.format(self.id),user)
                    ProposalUserAction.log_action(proposal,ProposalUserAction.ACTION_EXPIRED_APPROVAL_.format(proposal.id),user)
            except:
                raise

    def approval_extend(self,request,details):
        with transaction.atomic():
            try:
                if not request.user in self.allowed_assessors:
                    raise ValidationError('You do not have access to extend this approval')
                if not self.can_extend and self.can_action:
                    raise ValidationError('You cannot extend approval any further')
                self.renewal_count += 1
                self.extend_details = details.get('extend_details')
                self.expiry_date = datetime.date(self.expiry_date.year + self.current_proposal.application_type.max_renewal_period, self.expiry_date.month, self.expiry_date.day)
                today = timezone.now().date()
                if self.expiry_date <= today:
                    if not self.status == 'extended':
                        self.status = 'extended'
                        #send_approval_extend_email_notification(self)
                self.save()
                # Log proposal action
                self.log_user_action(ApprovalUserAction.ACTION_EXTEND_APPROVAL.format(self.id),request)
                # Log entry for organisation
                self.current_proposal.log_user_action(ProposalUserAction.ACTION_EXTEND_APPROVAL.format(self.current_proposal.id),request)
            except:
                raise


    def approval_cancellation(self,request,details):
        with transaction.atomic():
            try:
                if not request.user in self.allowed_assessors:
                    raise ValidationError('You do not have access to cancel this approval')
                if not self.can_reissue and self.can_action:
                    raise ValidationError('You cannot cancel approval if it is not current or suspended')
                self.cancellation_date = details.get('cancellation_date').strftime('%Y-%m-%d')
                self.cancellation_details = details.get('cancellation_details')
                cancellation_date = datetime.datetime.strptime(self.cancellation_date,'%Y-%m-%d')
                cancellation_date = cancellation_date.date()
                self.cancellation_date = cancellation_date # test hack
                today = timezone.now().date()
                if cancellation_date <= today:
                    if not self.status == 'cancelled':
                        self.status = 'cancelled'
                        self.set_to_cancel = False
                        send_approval_cancel_email_notification(self)
                else:
                    self.set_to_cancel = True
                self.save()
                # Log proposal action
                self.log_user_action(ApprovalUserAction.ACTION_CANCEL_APPROVAL.format(self.id),request)
                # Log entry for organisation
                self.current_proposal.log_user_action(ProposalUserAction.ACTION_CANCEL_APPROVAL.format(self.current_proposal.id),request)
            except:
                raise

    def approval_suspension(self,request,details):
        with transaction.atomic():
            try:
                if not request.user in self.allowed_assessors:
                    raise ValidationError('You do not have access to suspend this approval')
                if not self.can_reissue and self.can_action:
                    raise ValidationError('You cannot suspend approval if it is not current or suspended')
                if details.get('to_date'):
                    to_date= details.get('to_date').strftime('%d/%m/%Y')
                else:
                    to_date=''
                self.suspension_details = {
                    'from_date' : details.get('from_date').strftime('%d/%m/%Y'),
                    'to_date' : to_date,
                    'details': details.get('suspension_details'),
                }
                today = timezone.now().date()
                from_date = datetime.datetime.strptime(self.suspension_details['from_date'],'%d/%m/%Y')
                from_date = from_date.date()
                if from_date <= today:
                    if not self.status == 'suspended':
                        self.status = 'suspended'
                        self.set_to_suspend = False
                        self.save()
                        send_approval_suspend_email_notification(self)
                else:
                    self.set_to_suspend = True
                self.save()
                # Log approval action
                self.log_user_action(ApprovalUserAction.ACTION_SUSPEND_APPROVAL.format(self.id),request)
                # Log entry for proposal
                self.current_proposal.log_user_action(ProposalUserAction.ACTION_SUSPEND_APPROVAL.format(self.current_proposal.id),request)
            except:
                raise

    def reinstate_approval(self,request):
        with transaction.atomic():
            try:
                if not request.user in self.allowed_assessors:
                    raise ValidationError('You do not have access to reinstate this approval')
                if not self.can_reinstate:
                #if not self.status == 'suspended':
                    raise ValidationError('You cannot reinstate approval at this stage')
                today = timezone.now().date()
                if not self.can_reinstate and self.expiry_date>= today:
                #if not self.status == 'suspended' and self.expiry_date >= today:
                    raise ValidationError('You cannot reinstate approval at this stage')
                if self.status == 'cancelled':
                    self.cancellation_details =  ''
                    self.cancellation_date = None
                if self.status == 'surrendered':
                    self.surrender_details = {}
                if self.status == 'suspended':
                    self.suspension_details = {}

                self.status = 'current'
                #self.suspension_details = {}
                self.save()
                send_approval_reinstate_email_notification(self, request)
                # Log approval action
                self.log_user_action(ApprovalUserAction.ACTION_REINSTATE_APPROVAL.format(self.id),request)
                # Log entry for proposal
                self.current_proposal.log_user_action(ProposalUserAction.ACTION_REINSTATE_APPROVAL.format(self.current_proposal.id),request)
            except:
                raise

    def approval_surrender(self,request,details):
        with transaction.atomic():
            try:
                if not request.user.commercialoperator_organisations.filter(organisation_id = self.applicant_id):
                    if request.user not in self.allowed_assessors and not is_customer(request):
                        raise ValidationError('You do not have access to surrender this approval')
                if not self.can_reissue and self.can_action:
                    raise ValidationError('You cannot surrender approval if it is not current or suspended')
                self.surrender_details = {
                    'surrender_date' : details.get('surrender_date').strftime('%d/%m/%Y'),
                    'details': details.get('surrender_details'),
                }
                today = timezone.now().date()
                surrender_date = datetime.datetime.strptime(self.surrender_details['surrender_date'],'%d/%m/%Y')
                surrender_date = surrender_date.date()
                if surrender_date <= today:
                    if not self.status == 'surrendered':
                        self.status = 'surrendered'
                        self.set_to_surrender = False
                        self.save()
                        send_approval_surrender_email_notification(self)
                else:
                    self.set_to_surrender = True
                self.save()
                # Log approval action
                self.log_user_action(ApprovalUserAction.ACTION_SURRENDER_APPROVAL.format(self.id),request)
                # Log entry for proposal
                self.current_proposal.log_user_action(ProposalUserAction.ACTION_SURRENDER_APPROVAL.format(self.current_proposal.id),request)
            except:
                raise


class PreviewTempApproval(Approval):
    class Meta:
        app_label = 'commercialoperator'
        #unique_together= ('lodgement_number', 'issue_date')


class ApprovalLogEntry(CommunicationsLogEntry):
    approval = models.ForeignKey(Approval, related_name='comms_logs')

    class Meta:
        app_label = 'commercialoperator'

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.approval.id
        super(ApprovalLogEntry, self).save(**kwargs)

class ApprovalLogDocument(Document):
    log_entry = models.ForeignKey('ApprovalLogEntry',related_name='documents', null=True,)
    #approval = models.ForeignKey(Approval, related_name='comms_logs1')
    _file = models.FileField(upload_to=update_approval_comms_log_filename, null=True)
    #_file = models.FileField(upload_to=update_approval_doc_filename)

    class Meta:
        app_label = 'commercialoperator'

class ApprovalUserAction(UserAction):
    ACTION_CREATE_APPROVAL = "Create licence {}"
    ACTION_UPDATE_APPROVAL = "Create licence {}"
    ACTION_EXPIRE_APPROVAL = "Expire licence {}"
    ACTION_CANCEL_APPROVAL = "Cancel licence {}"
    ACTION_EXTEND_APPROVAL = "Extend licence {}"
    ACTION_SUSPEND_APPROVAL = "Suspend licence {}"
    ACTION_REINSTATE_APPROVAL = "Reinstate licence {}"
    ACTION_SURRENDER_APPROVAL = "surrender licence {}"
    ACTION_RENEW_APPROVAL = "Create renewal Application for licence {}"
    ACTION_AMEND_APPROVAL = "Create amendment Application for licence {}"


    class Meta:
        app_label = 'commercialoperator'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, approval, action, user):
        return cls.objects.create(
            approval=approval,
            who=user,
            what=str(action)
        )

    approval= models.ForeignKey(Approval, related_name='action_logs')

@receiver(pre_delete, sender=Approval)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        try:
            document.delete()
        except:
            pass

#import reversion
#reversion.register(Approval, follow=['documents', 'approval_set', 'action_logs'])
#reversion.register(ApprovalDocument)
#reversion.register(ApprovalLogDocument, follow=['documents'])
#reversion.register(ApprovalLogEntry)
#reversion.register(ApprovalUserAction)

import reversion
reversion.register(Approval, follow=['compliances', 'documents', 'comms_logs', 'action_logs'])
reversion.register(ApprovalDocument, follow=['licence_document', 'cover_letter_document', 'renewal_document'])
reversion.register(ApprovalLogEntry, follow=['documents'])
reversion.register(ApprovalLogDocument)
reversion.register(ApprovalUserAction)

