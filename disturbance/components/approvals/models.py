from __future__ import unicode_literals

import json
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
from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.licence.models import  Licence
from disturbance import exceptions
from disturbance.components.organisations.models import Organisation
from disturbance.components.proposals.models import Proposal, ProposalUserAction
from disturbance.components.main.models import CommunicationsLogEntry, UserAction, Document
from disturbance.components.approvals.email import (
    send_approval_expire_email_notification, 
    send_approval_cancel_email_notification,
    send_approval_suspend_email_notification
)
#from disturbance.components.approvals.email import send_referral_email_notification


def update_approval_doc_filename(instance, filename):
    return 'approvals/{}/documents/{}'.format(instance.id,filename)

class ApprovalDocument(Document):
    approval = models.ForeignKey('Approval',related_name='documents')
    _file = models.FileField(upload_to=update_approval_doc_filename)

    class Meta:
        app_label = 'disturbance'

class Approval(models.Model):
    STATUS_CHOICES = (
        ('current','Current'),
        ('expired','Expired'),
        ('cancelled','Cancelled'),
        ('surrendered','Surrendered'),
        ('suspended','Suspended')
    )
    status = models.CharField(max_length=40, choices=STATUS_CHOICES,
                                       default=STATUS_CHOICES[0][0])
    licence_document = models.ForeignKey(ApprovalDocument, blank=True, null=True, related_name='licence_document')
    cover_letter_document = models.ForeignKey(ApprovalDocument, blank=True, null=True, related_name='cover_letter_document')
    replaced_by = models.ForeignKey('self', blank=True, null=True)
    current_proposal = models.ForeignKey(Proposal,related_name = '+')
    activity = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    tenure = models.CharField(max_length=255,null=True)
    title = models.CharField(max_length=255)
    renewal_sent = models.BooleanField(default=False)
    issue_date = models.DateField()
    original_issue_date = models.DateField(auto_now_add=True)
    start_date = models.DateField()
    expiry_date = models.DateField()
    surrender_details = JSONField(blank=True,null=True)
    suspension_details = JSONField(blank=True,null=True)
    applicant = models.ForeignKey(Organisation,on_delete=models.PROTECT, related_name='disturbance_approvals')
    extracted_fields = JSONField(blank=True, null=True)
    cancellation_details = models.TextField(blank=True)
    cancellation_date = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'disturbance'

    def __str__(self):
        return self.reference

    @property
    def reference(self):
        return 'A{}'.format(self.id)

    @property
    def can_reissue(self):
        return self.status == 'current' or self.status == 'suspended'

    @property
    def allowed_assessors(self):
        return self.current_proposal.allowed_assessors

    @property
    def is_issued(self):
        return self.licence_number is not None and len(self.licence_number) > 0

    def generate_doc(self):
        from disturbance.components.approvals.pdf import create_approval_doc 
        self.licence_document = create_approval_doc(self,self.current_proposal)
        self.save()

    def log_user_action(self, action, request):
       return ApprovalUserAction.log_action(self, action, request.user)


    def expire_approval(self,user):
        with transaction.atomic():
            try:
                today = timezone.now().date()               
                if self.status == 'current' and self.expiry_date < today:
                    self.status = 'expired'
                    self.save()
                    send_approval_expire_email_notification(self)
                    proposal = self.current_proposal
                    ApprovalUserAction.log_action(self,ApprovalUserAction.ACTION_EXPIRE_APPROVAL.format(self.id),user)  
                    ProposalUserAction.log_action(proposal,ProposalUserAction.ACTION_LODGE_APPLICATION.format(proposal.id),user)  
            except:
                raise

    def approval_cancellation(self,request,details):
        with transaction.atomic():
            try:
                if not request.user in self.allowed_assessors:
                    raise ValidationError('You do not have access to cancel this approval')
                if not self.can_reissue:
                    raise ValidationError('You cannot cancel approval if it is not current or suspended')
                self.cancellation_date = details.get('cancellation_date').strftime('%Y-%m-%d')
                self.cancellation_details = details.get('cancellation_details')               
                self.status = 'cancelled'
                self.save()
                send_approval_cancel_email_notification(self, request)
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
                    raise ValidationError('You do not have access to cancel this approval')
                if not self.can_reissue:
                    raise ValidationError('You cannot cancel approval if it is not current or suspended')
                self.suspension_details = {
                    'from_date' : details.get('from_date').strftime('%d/%m/%Y'),
                    'to_date' : details.get('to_date').strftime('%d/%m/%Y'),
                    'details': details.get('suspension_details'),
                }             
                self.status = 'suspended'
                self.save()
                send_approval_suspend_email_notification(self, request)
                # Log proposal action
                self.log_user_action(ApprovalUserAction.ACTION_CANCEL_APPROVAL.format(self.id),request)
                # Log entry for organisation
                self.current_proposal.log_user_action(ProposalUserAction.ACTION_CANCEL_APPROVAL.format(self.current_proposal.id),request)
            except:
                raise

class ApprovalLogEntry(CommunicationsLogEntry):
    approval = models.ForeignKey(Approval, related_name='comms_logs')

    class Meta:
        app_label = 'disturbance'

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.approval.id
        super(ProposalLogEntry, self).save(**kwargs)

class ApprovalUserAction(UserAction):
    ACTION_CREATE_APPROVAL = "Create approval {}"
    ACTION_UPDATE_APPROVAL = "Create approval {}"
    ACTION_EXPIRE_APPROVAL = "Expire approval {}"
    ACTION_CANCEL_APPROVAL = "Cancel approval {}"

    
    class Meta:
        app_label = 'disturbance'
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
        document.delete()
