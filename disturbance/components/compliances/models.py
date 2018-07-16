
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
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.licence.models import  Licence
from disturbance import exceptions
from disturbance.components.organisations.models import Organisation
from disturbance.components.main.models import CommunicationsLogEntry, Region, UserAction, Document
from disturbance.components.proposals.models import ProposalRequirement
from disturbance.components.compliances.email import (
                        send_compliance_accept_email_notification,
                        send_amendment_email_notification,
                        send_reminder_email_notification)

class Compliance(models.Model):

    PROCESSING_STATUS_CHOICES = (('due', 'Due'), 
                                 ('future', 'Future'), 
                                 ('with_assessor', 'With Assessor'),
                                 ('approved', 'Approved'),
                                 )

    CUSTOMER_STATUS_CHOICES = (('due', 'Due'), 
                                 ('future', 'Future'), 
                                 ('with_assessor', 'Under Review'),
                                 ('approved', 'Approved'),
                                 )
    

    proposal = models.ForeignKey('disturbance.Proposal',related_name='compliances')
    approval = models.ForeignKey('disturbance.Approval',related_name='compliances')
    due_date = models.DateField()
    text = models.TextField(blank=True)
    processing_status = models.CharField(choices=PROCESSING_STATUS_CHOICES,max_length=20)
    customer_status = models.CharField(choices=CUSTOMER_STATUS_CHOICES,max_length=20, default=CUSTOMER_STATUS_CHOICES[1][0])
    assigned_to = models.ForeignKey(EmailUser,related_name='disturbance_compliance_assignments',null=True,blank=True)
    #requirement = models.TextField(null=True,blank=True)
    requirement = models.ForeignKey(ProposalRequirement, blank=True, null=True, related_name='compliance_requirement')
    lodgement_date = models.DateTimeField(blank=True, null=True)
    submitter = models.ForeignKey(EmailUser, blank=True, null=True, related_name='disturbance_compliances')


    class Meta:
        app_label = 'disturbance'

    @property
    def regions(self):
        return self.proposal.regions_list

    @property
    def activity(self):
        return self.proposal.activity

    @property
    def title(self):
        return self.proposal.title

    @property
    def holder(self):
        return self.proposal.applicant

    @property
    def reference(self):
        return 'C{0:06d}'.format(self.id)

    @property
    def allowed_assessors(self):
        return self.proposal.allowed_assessors

    @property
    def can_user_view(self):
        """
        :return: True if the application is in one of the editable status.
        """
        return self.customer_status == 'with_assessor' or self.customer_status == 'approved'


    @property        
    def amendment_requests(self):
        qs =ComplianceAmendmentRequest.objects.filter(compliance = self)
        return qs


    def submit(self,request):
        with transaction.atomic():
            try:               
                if self.processing_status == 'future' or 'due':
                    self.processing_status = 'with_assessor'
                    self.customer_status = 'with_assessor'
                    self.submitter = request.user

                    if request.FILES:
                        for f in request.FILES:
                            document = self.documents.create()
                            document.name = str(request.FILES[f])
                            document._file = request.FILES[f]
                            document.save()
                    if (self.amendment_requests):
                        qs = self.amendment_requests.filter(status = "requested")
                        if (qs):
                            for q in qs:    
                                q.status = 'amended'
                                q.save()
                #self.lodgement_date = datetime.datetime.strptime(timezone.now().strftime('%Y-%m-%d'),'%Y-%m-%d').date()
                self.lodgement_date = timezone.now()
                self.save() 
            except:
                raise

    def delete_document(self, request, document):
        with transaction.atomic():
            try:
                if document:
                    doc = self.documents.get(id=document[2])
                    doc.delete()
                return self
            except:
                raise ValidationError('Document not found')


    def assign_to(self, user,request):
        with transaction.atomic():
            self.assigned_to = user
            self.save()
            self.log_user_action(ComplianceUserAction.ACTION_ASSIGN_TO.format(user.get_full_name()),request)

    def unassign(self,request):
        with transaction.atomic():
            self.assigned_to = None 
            self.save()
            self.log_user_action(ComplianceUserAction.ACTION_UNASSIGN,request)

    def accept(self, request):
        with transaction.atomic():
            self.processing_status = 'approved'
            self.customer_status = 'approved'
            self.save()
            self.log_user_action(ComplianceUserAction.ACTION_CONCLUDE_REQUEST.format(self.id),request)
            send_compliance_accept_email_notification(self,request)


    def send_reminder(self,user):
        with transaction.atomic():
            today = timezone.now().date()
            try:
                if self.processing_status =='due':
                    if self.due_date < today and self.lodgement_date==None:
                        send_reminder_email_notification(self)
                        ComplianceUserAction.log_action(self,ComplianceUserAction.ACTION_CONCLUDE_REQUEST.format(self.id),user)
            except:
                raise
                        

    def log_user_action(self, action, request):
        return ComplianceUserAction.log_action(self, action, request.user)


def update_proposal_complaince_filename(instance, filename):
    return 'proposals/{}/compliance/{}/{}'.format(instance.compliance.proposal.id,instance.compliance.id,filename)


class ComplianceDocument(Document):
    compliance = models.ForeignKey('Compliance',related_name='documents')
    _file = models.FileField(upload_to=update_proposal_complaince_filename)


    class Meta:
        app_label = 'disturbance'

class ComplianceUserAction(UserAction):
    ACTION_CREATE = "Create compliance {}"
    ACTION_SUBMIT_REQUEST = "Submit compliance {}"
    ACTION_ASSIGN_TO = "Assign to {}"
    ACTION_UNASSIGN = "Unassign"
    ACTION_DECLINE_REQUEST = "Decline request"
    ACTION_ID_REQUEST_AMENDMENTS = "Request amendments"
    ACTION_REMINDER_SENT = "Reminder sent for compliance {}"
    # Assessors



    ACTION_CONCLUDE_REQUEST = "Conclude request {}"

    @classmethod
    def log_action(cls, compliance, action, user):
        return cls.objects.create(
            compliance=compliance,
            who=user,
            what=str(action)
        )

    compliance = models.ForeignKey(Compliance,related_name='action_logs')

    class Meta:
        app_label = 'disturbance'

class ComplianceLogEntry(CommunicationsLogEntry):
    compliance = models.ForeignKey(Compliance, related_name='comms_logs')

    def save(self, **kwargs):
        # save the request id if the reference not provided
        if not self.reference:
            self.reference = self.compliance.id
        super(ComplianceLogEntry, self).save(**kwargs)

    class Meta:
        app_label = 'disturbance'

def update_compliance_comms_log_filename(instance, filename):
    return 'proposals/{}/compliance/{}/communications/{}/{}'.format(instance.log_entry.compliance.proposal.id,instance.log_entry.compliance.id,instance.id,filename)


class ComplianceLogDocument(Document):
    log_entry = models.ForeignKey('ComplianceLogEntry',related_name='documents')
    _file = models.FileField(upload_to=update_compliance_comms_log_filename)

    class Meta:
        app_label = 'disturbance'

class CompRequest(models.Model):
    compliance = models.ForeignKey(Compliance)
    subject = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    officer = models.ForeignKey(EmailUser, null=True)

    class Meta:
        app_label = 'disturbance'

class ComplianceAmendmentRequest(CompRequest):
    STATUS_CHOICES = (('requested', 'Requested'), ('amended', 'Amended'))
    REASON_CHOICES = (('insufficient_detail', 'The information provided was insufficient'),
                      ('missing_information', 'There was missing information'),
                      ('other', 'Other'))
    status = models.CharField('Status', max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])

    class Meta:
        app_label = 'disturbance'

    def generate_amendment(self,request):
        with transaction.atomic():
          if self.status == 'requested':
            compliance = self.compliance
            if compliance.processing_status != 'due':
                compliance.processing_status = 'due'
                compliance.customer_status = 'due'
                compliance.save()
            # Create a log entry for the proposal
            compliance.log_user_action(ComplianceUserAction.ACTION_ID_REQUEST_AMENDMENTS,request)
            # Create a log entry for the organisation
            compliance.proposal.applicant.log_user_action(ComplianceUserAction.ACTION_ID_REQUEST_AMENDMENTS,request)
            send_amendment_email_notification(self,request, compliance)


def update_proposal_complaince_filename(instance, filename):
    return 'proposals/{}/compliance/{}/{}'.format(instance.compliance.proposal.id,instance.compliance.id,filename)



class ComplianceDocument(Document):
    compliance = models.ForeignKey('Compliance',related_name='documents')
    _file = models.FileField(upload_to=update_proposal_complaince_filename)


    class Meta:
        app_label = 'disturbance'