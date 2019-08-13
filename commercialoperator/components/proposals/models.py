from __future__ import unicode_literals

import json
import os
import datetime
import string
from dateutil.relativedelta import relativedelta
from django.db import models,transaction
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields.jsonb import JSONField
from django.utils import timezone
from django.contrib.sites.models import Site
from django.conf import settings
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import OrganisationAddress
from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.payments.models import Invoice
#from ledger.accounts.models import EmailUser
from ledger.licence.models import  Licence
from ledger.address.models import Country
from commercialoperator import exceptions
from commercialoperator.components.organisations.models import Organisation, OrganisationContact, UserDelegation
from commercialoperator.components.main.models import CommunicationsLogEntry, UserAction, Document, Region, District, Tenure, ApplicationType, Park, Activity, ActivityCategory, AccessType, Trail, Section, Zone, RequiredDocument#, RevisionedMixin
from commercialoperator.components.main.utils import get_department_user
from commercialoperator.components.proposals.email import send_referral_email_notification, send_proposal_decline_email_notification,send_proposal_approval_email_notification, send_amendment_email_notification
from commercialoperator.ordered_model import OrderedModel
from commercialoperator.components.proposals.email import send_submit_email_notification, send_external_submit_email_notification, send_approver_decline_email_notification, send_approver_approve_email_notification, send_referral_complete_email_notification, send_proposal_approver_sendback_email_notification, send_qaofficer_email_notification, send_qaofficer_complete_email_notification
import copy
import subprocess
from django.db.models import Q
from reversion.models import Version
from dirtyfields import DirtyFieldsMixin
from decimal import Decimal as D
import csv

import logging
logger = logging.getLogger(__name__)


def update_proposal_doc_filename(instance, filename):
    return '{}/proposals/{}/documents/{}'.format(settings.MEDIA_APP_DIR, instance.proposal.id,filename)

def update_onhold_doc_filename(instance, filename):
    return '{}/proposals/{}/on_hold/{}'.format(settings.MEDIA_APP_DIR, instance.proposal.id,filename)

def update_qaofficer_doc_filename(instance, filename):
    return '{}/proposals/{}/qaofficer/{}'.format(settings.MEDIA_APP_DIR, instance.proposal.id,filename)

def update_referral_doc_filename(instance, filename):
    return '{}/proposals/{}/referral/{}'.format(settings.MEDIA_APP_DIR, instance.referral.proposal.id,filename)

def update_proposal_required_doc_filename(instance, filename):
    return '{}/proposals/{}/required_documents/{}'.format(settings.MEDIA_APP_DIR, instance.proposal.id,filename)

def update_requirement_doc_filename(instance, filename):
    return '{}/proposals/{}/requirement_documents/{}'.format(settings.MEDIA_APP_DIR, instance.requirement.proposal.id,filename)

def update_proposal_comms_log_filename(instance, filename):
    return '{}/proposals/{}/communications/{}'.format(settings.MEDIA_APP_DIR, instance.log_entry.proposal.id,filename)

def application_type_choicelist():
    try:
        return [( (choice.name), (choice.name) ) for choice in ApplicationType.objects.filter(visible=True)]
    except:
        # required because on first DB tables creation, there are no ApplicationType objects -- setting a default value
        return ( ('T Class', 'T Class'), )

class ProposalType(models.Model):
    #name = models.CharField(verbose_name='Application name (eg. commercialoperator, Apiary)', max_length=24)
    #application_type = models.ForeignKey(ApplicationType, related_name='aplication_types')
    description = models.CharField(max_length=256, blank=True, null=True)
    #name = models.CharField(verbose_name='Application name (eg. commercialoperator, Apiary)', max_length=24, choices=application_type_choicelist(), default=application_type_choicelist()[0][0])
    name = models.CharField(verbose_name='Application name (eg. T Class, Filming, Event, E Class)', max_length=64, choices=application_type_choicelist(), default='T Class')
    schema = JSONField(default=[{}])
    #activities = TaggableManager(verbose_name="Activities",help_text="A comma-separated list of activities.")
    #site = models.OneToOneField(Site, default='1')
    replaced_by = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    version = models.SmallIntegerField(default=1, blank=False, null=False)

    def __str__(self):
        return '{} - v{}'.format(self.name, self.version)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('name', 'version')

class TaggedProposalAssessorGroupRegions(TaggedItemBase):
    content_object = models.ForeignKey("ProposalAssessorGroup")

    class Meta:
        app_label = 'commercialoperator'

class TaggedProposalAssessorGroupActivities(TaggedItemBase):
    content_object = models.ForeignKey("ProposalAssessorGroup")

    class Meta:
        app_label = 'commercialoperator'

class ProposalAssessorGroup(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(EmailUser)
    region = models.ForeignKey(Region, null=True, blank=True)
    default = models.BooleanField(default=False)

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Assessor Group"
        verbose_name_plural = "Application Assessor Group"

    def __str__(self):
        return self.name

    def clean(self):
        try:
            default = ProposalAssessorGroup.objects.get(default=True)
        except ProposalAssessorGroup.DoesNotExist:
            default = None

        if self.pk:
            if not self.default and not self.region:
                raise ValidationError('Only default can have no region set for proposal assessor group. Please specifiy region')
#            elif default and not self.default:
#                raise ValidationError('There can only be one default proposal assessor group')
        else:
            if default and self.default:
                raise ValidationError('There can only be one default proposal assessor group')

    def member_is_assigned(self,member):
        for p in self.current_proposals:
            if p.assigned_officer == member:
                return True
        return False

    @property
    def current_proposals(self):
        assessable_states = ['with_assessor','with_referral','with_assessor_requirements']
        return Proposal.objects.filter(processing_status__in=assessable_states)

    @property
    def members_email(self):
        return [i.email for i in self.members.all()]

class TaggedProposalApproverGroupRegions(TaggedItemBase):
    content_object = models.ForeignKey("ProposalApproverGroup")

    class Meta:
        app_label = 'commercialoperator'

class TaggedProposalApproverGroupActivities(TaggedItemBase):
    content_object = models.ForeignKey("ProposalApproverGroup")

    class Meta:
        app_label = 'commercialoperator'

class ProposalApproverGroup(models.Model):
    name = models.CharField(max_length=255)
    #members = models.ManyToManyField(EmailUser,blank=True)
    #regions = TaggableManager(verbose_name="Regions",help_text="A comma-separated list of regions.",through=TaggedProposalApproverGroupRegions,related_name = "+",blank=True)
    #activities = TaggableManager(verbose_name="Activities",help_text="A comma-separated list of activities.",through=TaggedProposalApproverGroupActivities,related_name = "+",blank=True)
    members = models.ManyToManyField(EmailUser)
    region = models.ForeignKey(Region, null=True, blank=True)
    default = models.BooleanField(default=False)

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Approver Group"
        verbose_name_plural = "Application Approver Group"

    def __str__(self):
        return self.name

    def clean(self):
        try:
            default = ProposalApproverGroup.objects.get(default=True)
        except ProposalApproverGroup.DoesNotExist:
            default = None

        if self.pk:
            if not self.default and not self.region:
                raise ValidationError('Only default can have no region set for proposal assessor group. Please specifiy region')

#            if int(self.pk) != int(default.id):
#                if default and self.default:
#                    raise ValidationError('There can only be one default proposal approver group')
        else:
            if default and self.default:
                raise ValidationError('There can only be one default proposal approver group')

    def member_is_assigned(self,member):
        for p in self.current_proposals:
            if p.assigned_approver == member:
                return True
        return False

    @property
    def current_proposals(self):
        assessable_states = ['with_approver']
        return Proposal.objects.filter(processing_status__in=assessable_states)

    @property
    def members_email(self):
        return [i.email for i in self.members.all()]


class DefaultDocument(Document):
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    visible = models.BooleanField(default=True) # to prevent deletion on file system, hidden and still be available in history

    class Meta:
        app_label = 'commercialoperator'
        abstract =True

    def delete(self):
        if self.can_delete:
            return super(DefaultDocument, self).delete()
        logger.info('Cannot delete existing document object after Application has been submitted (including document submitted before Application pushback to status Draft): {}'.format(self.name))



class ProposalDocument(Document):
    proposal = models.ForeignKey('Proposal',related_name='documents')
    _file = models.FileField(upload_to=update_proposal_doc_filename)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Document"

class OnHoldDocument(Document):
    proposal = models.ForeignKey('Proposal',related_name='onhold_documents')
    _file = models.FileField(upload_to=update_onhold_doc_filename)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    visible = models.BooleanField(default=True) # to prevent deletion on file system, hidden and still be available in history

    def delete(self):
        if self.can_delete:
            return super(ProposalDocument, self).delete()

#Documents on Activities(land)and Activities(Marine) tab for T-Class related to required document questions
class ProposalRequiredDocument(Document):
    proposal = models.ForeignKey('Proposal',related_name='required_documents')
    _file = models.FileField(upload_to=update_proposal_required_doc_filename)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    required_doc = models.ForeignKey('RequiredDocument',related_name='proposals')

    def delete(self):
        if self.can_delete:
            return super(ProposalRequiredDocument, self).delete()
        logger.info('Cannot delete existing document object after Application has been submitted (including document submitted before Application pushback to status Draft): {}'.format(self.name))

    class Meta:
        app_label = 'commercialoperator'

class QAOfficerDocument(Document):
    proposal = models.ForeignKey('Proposal',related_name='qaofficer_documents')
    _file = models.FileField(upload_to=update_qaofficer_doc_filename)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    visible = models.BooleanField(default=True) # to prevent deletion on file system, hidden and still be available in history

    def delete(self):
        if self.can_delete:
            return super(QAOfficerDocument, self).delete()
        logger.info('Cannot delete existing document object after Application has been submitted (including document submitted before Application pushback to status Draft): {}'.format(self.name))

    class Meta:
        app_label = 'commercialoperator'


class ReferralDocument(Document):
    referral = models.ForeignKey('Referral',related_name='referral_documents')
    _file = models.FileField(upload_to=update_referral_doc_filename)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted

    def delete(self):
        if self.can_delete:
            return super(ProposalDocument, self).delete()
        logger.info('Cannot delete existing document object after Application has been submitted (including document submitted before Application pushback to status Draft): {}'.format(self.name))

    class Meta:
        app_label = 'commercialoperator'

class RequirementDocument(Document):
    requirement = models.ForeignKey('ProposalRequirement',related_name='requirement_documents')
    _file = models.FileField(upload_to=update_requirement_doc_filename)
    input_name = models.CharField(max_length=255,null=True,blank=True)
    can_delete = models.BooleanField(default=True) # after initial submit prevent document from being deleted
    visible = models.BooleanField(default=True) # to prevent deletion on file system, hidden and still be available in history

    def delete(self):
        if self.can_delete:
            return super(RequirementDocument, self).delete()


class ProposalApplicantDetails(models.Model):
    first_name = models.CharField(max_length=24, blank=True, default='')

    class Meta:
        app_label = 'commercialoperator'


class ProposalActivitiesLand(models.Model):
    activities_land = models.CharField(max_length=24, blank=True, default='')

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Activity (Land)"
        verbose_name_plural = "Application Activities (Land)"


class ProposalActivitiesMarine(models.Model):
    activities_marine = models.CharField(max_length=24, blank=True, default='')

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Activity (Marine)"
        verbose_name_plural = "Application Activities (Marine)"


@python_2_unicode_compatible
class ParkEntry(models.Model):
    park = models.ForeignKey('Park', related_name='park_entries')
    proposal = models.ForeignKey('Proposal', related_name='park_entries')
    arrival_date = models.DateField()
    number_adults = models.PositiveSmallIntegerField('No. of Adults', null=True, blank=True)
    number_children = models.PositiveSmallIntegerField('No. of Children', null=True, blank=True)
    number_seniors = models.PositiveSmallIntegerField('No. of Senior Citizens', null=True, blank=True)
    number_free_of_charge = models.PositiveSmallIntegerField('No. of Individuals Free of Charge', null=True, blank=True)

    class Meta:
        ordering = ['park__name']
        app_label = 'commercialoperator'
        verbose_name = "Park Entry"
        verbose_name_plural = "Park Entries"
        #unique_together = ('id', 'proposal',)

    def __str__(self):
        return self.park.name

    @property
    def park_prices(self):
        return self.park.park_prices

    @property
    def price_adult(self):
        return (self.park_prices.adult * self.number_adults)

    @property
    def price_child(self):
        return (self.park_prices.child * self.number_children)

    @property
    def price_senior(self):
        return (self.park_prices.senior * self.number_senior)

    @property
    def price_net(self):
        return (self.price_adult + self.price_child + self.price_senior)


class Proposal(DirtyFieldsMixin, RevisionedMixin):
#class Proposal(DirtyFieldsMixin, models.Model):
    APPLICANT_TYPE_ORGANISATION = 'ORG'
    APPLICANT_TYPE_PROXY = 'PRX'
    APPLICANT_TYPE_SUBMITTER = 'SUB'

    CUSTOMER_STATUS_TEMP = 'temp'
    CUSTOMER_STATUS_WITH_ASSESSOR = 'with_assessor'
    CUSTOMER_STATUS_AMENDMENT_REQUIRED = 'amendment_required'
    CUSTOMER_STATUS_APPROVED = 'approved'
    CUSTOMER_STATUS_DECLINED = 'declined'
    CUSTOMER_STATUS_DISCARDED = 'discarded'
    CUSTOMER_STATUS_CHOICES = ((CUSTOMER_STATUS_TEMP, 'Temporary'), ('draft', 'Draft'),
                               (CUSTOMER_STATUS_WITH_ASSESSOR, 'Under Review'),
                               (CUSTOMER_STATUS_AMENDMENT_REQUIRED, 'Amendment Required'),
                               (CUSTOMER_STATUS_APPROVED, 'Approved'),
                               (CUSTOMER_STATUS_DECLINED, 'Declined'),
                               (CUSTOMER_STATUS_DISCARDED, 'Discarded'),
                               )

    # List of statuses from above that allow a customer to edit an application.
    CUSTOMER_EDITABLE_STATE = ['temp',
                                'draft',
                                'amendment_required',
                            ]

    # List of statuses from above that allow a customer to view an application (read-only)
    CUSTOMER_VIEWABLE_STATE = ['with_assessor', 'under_review', 'id_required', 'returns_required', 'approved', 'declined']

    PROCESSING_STATUS_TEMP = 'temp'
    PROCESSING_STATUS_DRAFT = 'draft'
    PROCESSING_STATUS_WITH_ASSESSOR = 'with_assessor'
    PROCESSING_STATUS_ONHOLD = 'on_hold'
    PROCESSING_STATUS_WITH_QA_OFFICER = 'with_qa_officer'
    PROCESSING_STATUS_WITH_REFERRAL = 'with_referral'
    PROCESSING_STATUS_WITH_ASSESSOR_REQUIREMENTS = 'with_assessor_requirements'
    PROCESSING_STATUS_WITH_APPROVER = 'with_approver'
    PROCESSING_STATUS_RENEWAL = 'renewal'
    PROCESSING_STATUS_LICENCE_AMENDMENT = 'licence_amendment'
    PROCESSING_STATUS_AWAITING_APPLICANT_RESPONSE = 'awaiting_applicant_respone'
    PROCESSING_STATUS_AWAITING_ASSESSOR_RESPONSE = 'awaiting_assessor_response'
    PROCESSING_STATUS_AWAITING_RESPONSES = 'awaiting_responses'
    PROCESSING_STATUS_READY_FOR_CONDITIONS = 'ready_for_conditions'
    PROCESSING_STATUS_READY_TO_ISSUE = 'ready_to_issue'
    PROCESSING_STATUS_APPROVED = 'approved'
    PROCESSING_STATUS_DECLINED = 'declined'
    PROCESSING_STATUS_DISCARDED = 'discarded'
    PROCESSING_STATUS_CHOICES = ((PROCESSING_STATUS_TEMP, 'Temporary'),
                                 (PROCESSING_STATUS_DRAFT, 'Draft'),
                                 (PROCESSING_STATUS_WITH_ASSESSOR, 'With Assessor'),
                                 (PROCESSING_STATUS_ONHOLD, 'On Hold'),
                                 (PROCESSING_STATUS_WITH_QA_OFFICER, 'With QA Officer'),
                                 (PROCESSING_STATUS_WITH_REFERRAL, 'With Referral'),
                                 (PROCESSING_STATUS_WITH_ASSESSOR_REQUIREMENTS, 'With Assessor (Requirements)'),
                                 (PROCESSING_STATUS_WITH_APPROVER, 'With Approver'),
                                 (PROCESSING_STATUS_RENEWAL, 'Renewal'),
                                 (PROCESSING_STATUS_LICENCE_AMENDMENT, 'Licence Amendment'),
                                 (PROCESSING_STATUS_AWAITING_APPLICANT_RESPONSE, 'Awaiting Applicant Response'),
                                 (PROCESSING_STATUS_AWAITING_ASSESSOR_RESPONSE, 'Awaiting Assessor Response'),
                                 (PROCESSING_STATUS_AWAITING_RESPONSES, 'Awaiting Responses'),
                                 (PROCESSING_STATUS_READY_FOR_CONDITIONS, 'Ready for Conditions'),
                                 (PROCESSING_STATUS_READY_TO_ISSUE, 'Ready to Issue'),
                                 (PROCESSING_STATUS_APPROVED, 'Approved'),
                                 (PROCESSING_STATUS_DECLINED, 'Declined'),
                                 (PROCESSING_STATUS_DISCARDED, 'Discarded'),
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

#    PROPOSAL_STATE_NEW_LICENCE = 'New Licence'
#    PROPOSAL_STATE_AMENDMENT = 'Amendment'
#    PROPOSAL_STATE_RENEWAL = 'Renewal'
#    PROPOSAL_STATE_CHOICES = (
#        (1, PROPOSAL_STATE_NEW_LICENCE),
#        (2, PROPOSAL_STATE_AMENDMENT),
#        (3, PROPOSAL_STATE_RENEWAL),
#    )

    APPLICATION_TYPE_CHOICES = (
        ('new_proposal', 'New Application'),
        ('amendment', 'Amendment'),
        ('renewal', 'Renewal'),
        ('external', 'External'),
    )

    proposal_type = models.CharField('Application Status Type', max_length=40, choices=APPLICATION_TYPE_CHOICES,
                                        default=APPLICATION_TYPE_CHOICES[0][0])
    #proposal_state = models.PositiveSmallIntegerField('Proposal state', choices=PROPOSAL_STATE_CHOICES, default=1)

    data = JSONField(blank=True, null=True)
    assessor_data = JSONField(blank=True, null=True)
    comment_data = JSONField(blank=True, null=True)
    schema = JSONField(blank=False, null=False)
    proposed_issuance_approval = JSONField(blank=True, null=True)
    #hard_copy = models.ForeignKey(Document, blank=True, null=True, related_name='hard_copy')

    customer_status = models.CharField('Customer Status', max_length=40, choices=CUSTOMER_STATUS_CHOICES,
                                       default=CUSTOMER_STATUS_CHOICES[1][0])
    #applicant = models.ForeignKey(Organisation, blank=True, null=True, related_name='proposals')
    org_applicant = models.ForeignKey(
        Organisation,
        blank=True,
        null=True,
        related_name='org_applications')
    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    lodgement_sequence = models.IntegerField(blank=True, default=0)
    #lodgement_date = models.DateField(blank=True, null=True)
    lodgement_date = models.DateTimeField(blank=True, null=True)

    proxy_applicant = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_proxy')
    submitter = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_proposals')

    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_proposals_assigned', on_delete=models.SET_NULL)
    assigned_approver = models.ForeignKey(EmailUser, blank=True, null=True, related_name='commercialoperator_proposals_approvals', on_delete=models.SET_NULL)
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[1][0])
    prev_processing_status = models.CharField(max_length=30, blank=True, null=True)
    id_check_status = models.CharField('Identification Check Status', max_length=30, choices=ID_CHECK_STATUS_CHOICES,
                                       default=ID_CHECK_STATUS_CHOICES[0][0])
    compliance_check_status = models.CharField('Return Check Status', max_length=30, choices=COMPLIANCE_CHECK_STATUS_CHOICES,
                                            default=COMPLIANCE_CHECK_STATUS_CHOICES[0][0])
    character_check_status = models.CharField('Character Check Status', max_length=30,
                                              choices=CHARACTER_CHECK_STATUS_CHOICES,
                                              default=CHARACTER_CHECK_STATUS_CHOICES[0][0])
    review_status = models.CharField('Review Status', max_length=30, choices=REVIEW_STATUS_CHOICES,
                                     default=REVIEW_STATUS_CHOICES[0][0])

    approval = models.ForeignKey('commercialoperator.Approval',null=True,blank=True)

    previous_application = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    proposed_decline_status = models.BooleanField(default=False)
    #qaofficer_referral = models.BooleanField(default=False)
    #qaofficer_referral = models.OneToOneField('QAOfficerReferral', blank=True, null=True)
    # Special Fields
    title = models.CharField(max_length=255,null=True,blank=True)
    activity = models.CharField(max_length=255,null=True,blank=True)
    #region = models.CharField(max_length=255,null=True,blank=True)
    tenure = models.CharField(max_length=255,null=True,blank=True)
    #activity = models.ForeignKey(Activity, null=True, blank=True)
    region = models.ForeignKey(Region, null=True, blank=True)
    district = models.ForeignKey(District, null=True, blank=True)
    #tenure = models.ForeignKey(Tenure, null=True, blank=True)
    application_type = models.ForeignKey(ApplicationType)
    approval_level = models.CharField('Activity matrix approval level', max_length=255,null=True,blank=True)
    approval_level_document = models.ForeignKey(ProposalDocument, blank=True, null=True, related_name='approval_level_document')
    approval_comment = models.TextField(blank=True)
    #If the proposal is created as part of migration of approvals
    migrated=models.BooleanField(default=False)


    # common
    #applicant_details = models.OneToOneField(ProposalApplicantDetails, blank=True, null=True) #, related_name='applicant_details')
    training_completed = models.BooleanField(default=False)
    #payment = models.OneToOneField(ProposalPayment, blank=True, null=True)
    #confirmation = models.OneToOneField(ProposalConfirmation, blank=True, null=True)

    # T Class
    activities_land = models.OneToOneField(ProposalActivitiesLand, blank=True, null=True) #, related_name='activities_land')
    activities_marine = models.OneToOneField(ProposalActivitiesMarine, blank=True, null=True) #, related_name='activities_marine')
    #other_details = models.OneToOneField(ProposalOtherDetails, blank=True, null=True, related_name='proposal')
    #online_training = models.OneToOneField(ProposalOnlineTraining, blank=True, null=True)

    # Filming
    #activity = models.OneToOneField(ProposalActivity, blank=True, null=True)
    #access = models.OneToOneField(ProposalAccess, blank=True, null=True)
    #equipment = models.OneToOneField(ProposalEquipment, blank=True, null=True)
    #other_details = models.OneToOneField(ProposalOtherDetails, blank=True, null=True)
    #online_training = models.OneToOneField(ProposalOnlineTraining, blank=True, null=True)

    # Event
    #activities = models.OneToOneField(ProposalActivities, blank=True, null=True)
    #event_management = models.OneToOneField(ProposalEventManagement, blank=True, null=True)
    #vehicles_vessels = models.OneToOneField(ProposalVehiclesVessels, blank=True, null=True)
    #other_details = models.OneToOneField(ProposalOtherDetails, blank=True, null=True)
    #online_training = models.OneToOneField(ProposalOnlineTraining, blank=True, null=True)

    fee_invoice_reference = models.CharField(max_length=50, null=True, blank=True, default='')

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application"
        verbose_name_plural = "Applications"

    def __str__(self):
        return str(self.id)

    #Append 'P' to Proposal id to generate Lodgement number. Lodgement number and lodgement sequence are used to generate Reference.
    def save(self, *args, **kwargs):
        orig_processing_status = self._original_state['processing_status']
        super(Proposal, self).save(*args,**kwargs)
        if self.processing_status != orig_processing_status:
            #import ipdb; ipdb.set_trace()
            self.save(version_comment='processing_status: {}'.format(self.processing_status))

        if self.lodgement_number == '' and self.application_type.name != 'E Class':
            new_lodgment_id = 'A{0:06d}'.format(self.pk)
            self.lodgement_number = new_lodgment_id
            self.save(version_comment='processing_status: {}'.format(self.processing_status))

    @property
    def fee_paid(self):
        return True if self.fee_invoice_reference else False

    @property
    def fee_amount(self):
        return Invoice.objects.get(reference=self.fee_invoice_reference).amount if self.fee_paid else None

    @property
    def reference(self):
        return '{}-{}'.format(self.lodgement_number, self.lodgement_sequence)

    @property
    def reversion_ids(self):
        current_revision_id = Version.objects.get_for_object(self).first().revision_id
        versions = Version.objects.get_for_object(self).select_related("revision__user").filter(Q(revision__comment__icontains='status') | Q(revision_id=current_revision_id))
        version_ids = [[i.id,i.revision.date_created] for i in versions]
        return [dict(cur_version_id=version_ids[0][0], prev_version_id=version_ids[i+1][0], created=version_ids[i][1]) for i in range(len(version_ids)-1)]

    @property
    def applicant(self):
        if self.org_applicant:
            return self.org_applicant.organisation.name
        elif self.proxy_applicant:
            return "{} {}".format(
                self.proxy_applicant.first_name,
                self.proxy_applicant.last_name)
        else:
            return "{} {}".format(
                self.submitter.first_name,
                self.submitter.last_name)

    @property
    def applicant_details(self):
        if self.org_applicant:
            return '{} \n{}'.format(
                self.org_applicant.organisation.name,
                self.org_applicant.address)
        elif self.proxy_applicant:
            return "{} {}\n{}".format(
                self.proxy_applicant.first_name,
                self.proxy_applicant.last_name,
                self.proxy_applicant.addresses.all().first())
        else:
            return "{} {}\n{}".format(
                self.submitter.first_name,
                self.submitter.last_name,
                self.submitter.addresses.all().first())

    @property
    def applicant_address(self):
        if self.org_applicant:
            return self.org_applicant.address
        elif self.proxy_applicant:
            #return self.proxy_applicant.addresses.all().first()
            return self.proxy_applicant.residential_address
        else:
            #return self.submitter.addresses.all().first()
            return self.submitter.residential_address

    @property
    def applicant_id(self):
        if self.org_applicant:
            return self.org_applicant.id
        elif self.proxy_applicant:
            return self.proxy_applicant.id
        else:
            return self.submitter.id

    @property
    def applicant_type(self):
        if self.org_applicant:
            return self.APPLICANT_TYPE_ORGANISATION
        elif self.proxy_applicant:
            return self.APPLICANT_TYPE_PROXY
        else:
            return self.APPLICANT_TYPE_SUBMITTER

    @property
    def applicant_field(self):
        if self.org_applicant:
            return 'org_applicant'
        elif self.proxy_applicant:
            return 'proxy_applicant'
        else:
            return 'submitter'

    def qa_officers(self, name=None):
        if not name:
            return QAOfficerGroup.objects.get(default=True).members.all().values_list('email', flat=True)
        else:
            return QAOfficerGroup.objects.get(name=name).members.all().values_list('email', flat=True)

    @property
    def get_history(self):
        """ Return the prev proposal versions """
        l = []
        p = copy.deepcopy(self)
        while (p.previous_application):
            l.append( dict(id=p.previous_application.id, modified=p.previous_application.modified_date) )
            p = p.previous_application
        return l

#    def _get_history(self):
#        """ Return the prev proposal versions """
#        l = []
#        p = copy.deepcopy(self)
#        while (p.previous_application):
#            l.append( [p.id, p.previous_application.id] )
#            p = p.previous_application
#        return l

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

    @property
    def land_parks(self):
        return self.parks.filter(park__park_type='land')

    @property
    def marine_parks(self):
        return self.parks.filter(park__park_type='marine')

    @property
    def regions_list(self):
        #return self.region.split(',') if self.region else []
        return [self.region.name] if self.region else []

    @property
    def assessor_assessment(self):
        qs=self.assessment.filter(referral_assessment=False, referral_group=None)
        if qs:
            return qs[0]
        else:
            return None

    @property
    def referral_assessments(self):
        qs=self.assessment.filter(referral_assessment=True, referral_group__isnull=False)
        if qs:
            return qs
        else:
            return None


    @property
    def permit(self):
        return self.approval.licence_document._file.url if self.approval else None

    @property
    def allowed_assessors(self):
        if self.processing_status == 'with_approver':
            group = self.__approver_group()
        elif self.processing_status =='with_qa_officer':
            group = QAOfficerGroup.objects.get(default=True)
        else:
            group = self.__assessor_group()
        return group.members.all() if group else []

    @property
    def compliance_assessors(self):
        group = self.__assessor_group()
        return group.members.all() if group else []

    @property
    def can_officer_process(self):
        """
        :return: True if the application is in one of the processable status for Assessor role.
        """
        #officer_view_state = ['draft','approved','declined','temp','discarded']
        officer_view_state = ['draft','approved','declined','temp','discarded', 'with_referral', 'with_qa_officer']
        if self.processing_status in officer_view_state:
            return False
        else:
            return True

    @property
    def amendment_requests(self):
        qs =AmendmentRequest.objects.filter(proposal = self)
        return qs

    @property
    def search_data(self):
        search_data={}
        parks=[]
        trails=[]
        activities=[]
        vehicles=[]
        vessels=[]
        accreditations=[]
        for p in self.parks.all():
            parks.append(p.park.name)
            if p.park.park_type=='land':
                for a in p.activities.all():
                    activities.append(a.activity_name)
            if p.park.park_type=='marine':
                for z in p.zones.all():
                    for a in z.park_activities.all():
                        activities.append(a.activity_name)
        for t in self.trails.all():
            trails.append(t.trail.name)
            for s in t.sections.all():
                for ts in s.trail_activities.all():
                  activities.append(ts.activity_name)
        for v in self.vehicles.all():
            vehicles.append(v.rego)
        for vs in self.vessels.all():
            vessels.append(vs.spv_no)
        search_data.update({'parks': parks})
        search_data.update({'trails': trails})
        search_data.update({'vehicles': vehicles})
        search_data.update({'vessels': vessels})
        search_data.update({'activities': activities})

        try:
            other_details=ProposalOtherDetails.objects.get(proposal=self)
            search_data.update({'other_details': other_details.other_comments})
            search_data.update({'mooring': other_details.mooring})
            for acr in other_details.accreditations.all():
                accreditations.append(acr.get_accreditation_type_display())
            search_data.update({'accreditations': accreditations})
        except ProposalOtherDetails.DoesNotExist:
            search_data.update({'other_details': []})
            search_data.update({'mooring': []})
            search_data.update({'accreditations':[]})
        return search_data

    @property
    def selected_parks_activities(self):
        #list of selected parks and activities (to print on licence pdf)
        selected_parks_activities=[]
        for p in self.parks.all():
            park_activities=[]
            #parks.append(p.park.name)
            if p.park.park_type=='land':
                for a in p.activities.all():
                    park_activities.append(a.activity_name)
                selected_parks_activities.append({'park': p.park.name, 'activities': park_activities})
            if p.park.park_type=='marine':
                zone_activities=[]
                for z in p.zones.all():
                    for a in z.park_activities.all():
                        zone_activities.append(a.activity_name)
                    selected_parks_activities.append({'park': '{} - {}'.format(p.park.name, z.zone.name), 'activities': park_activities})
        for t in self.trails.all():
            #trails.append(t.trail.name)
            #trail_activities=[]
            for s in t.sections.all():
                trail_activities=[]
                for ts in s.trail_activities.all():
                  trail_activities.append(ts.activity_name)
                selected_parks_activities.append({'park': '{} - {}'.format(t.trail.name, s.section.name), 'activities': trail_activities})
        return selected_parks_activities

    def __assessor_group(self):
        # TODO get list of assessor groups based on region and activity
        if self.region and self.activity:
            try:
                check_group = ProposalAssessorGroup.objects.filter(
                    #activities__name__in=[self.activity],
                    region__name__in=self.regions_list
                ).distinct()
                if check_group:
                    return check_group[0]
            except ProposalAssessorGroup.DoesNotExist:
                pass
        default_group = ProposalAssessorGroup.objects.get(default=True)

        return default_group


    def __approver_group(self):
        # TODO get list of approver groups based on region and activity
        if self.region and self.activity:
            try:
                check_group = ProposalApproverGroup.objects.filter(
                    #activities__name__in=[self.activity],
                    region__name__in=self.regions_list
                ).distinct()
                if check_group:
                    return check_group[0]
            except ProposalApproverGroup.DoesNotExist:
                pass
        default_group = ProposalApproverGroup.objects.get(default=True)

        return default_group

    def __check_proposal_filled_out(self):
        if not self.data:
            raise exceptions.ProposalNotComplete()
        missing_fields = []
        required_fields = {
        #    'region':'Region/District',
        #    'title': 'Title',
        #    'activity': 'Activity'
        }
        #import ipdb; ipdb.set_trace()
        for k,v in required_fields.items():
            val = getattr(self,k)
            if not val:
                missing_fields.append(v)
        return missing_fields

    @property
    def assessor_recipients(self):
        recipients = []
        #import ipdb; ipdb.set_trace()
        try:
            recipients = ProposalAssessorGroup.objects.get(region=self.region).members_email
        except:
            recipients = ProposalAssessorGroup.objects.get(default=True).members_email

        #if self.submitter.email not in recipients:
        #    recipients.append(self.submitter.email)
        return recipients

    @property
    def approver_recipients(self):
        recipients = []
        try:
            recipients = ProposalApproverGroup.objects.get(region=self.region).members_email
        except:
            recipients = ProposalApproverGroup.objects.get(default=True).members_email

        #if self.submitter.email not in recipients:
        #    recipients.append(self.submitter.email)
        return recipients


    def can_assess(self,user):
        #if self.processing_status == 'on_hold' or self.processing_status == 'with_assessor' or self.processing_status == 'with_referral' or self.processing_status == 'with_assessor_requirements':
        if self.processing_status in ['on_hold', 'with_qa_officer', 'with_assessor', 'with_referral', 'with_assessor_requirements']:
            return self.__assessor_group() in user.proposalassessorgroup_set.all()
        elif self.processing_status == 'with_approver':
            return self.__approver_group() in user.proposalapprovergroup_set.all()
        else:
            return False

    #To allow/ prevent internal user to edit activities (Land and Marine) for T-class licence
    #still need to check to assessor mode in on or not
    def can_edit_activities(self,user):
        if self.processing_status == 'with_assessor' or self.processing_status == 'with_assessor_requirements':
            return self.__assessor_group() in user.proposalassessorgroup_set.all()
        elif self.processing_status == 'with_approver':
            return self.__approver_group() in user.proposalapprovergroup_set.all()
        else:
            return False

    def assessor_comments_view(self,user):

        if self.processing_status == 'with_assessor' or self.processing_status == 'with_referral' or self.processing_status == 'with_assessor_requirements' or self.processing_status == 'with_approver':
            try:
                referral = Referral.objects.get(proposal=self,referral=user)
            except:
                referral = None
            if referral:
                return True
            elif self.__assessor_group() in user.proposalassessorgroup_set.all():
                return True
            elif self.__approver_group() in user.proposalapprovergroup_set.all():
                return True
            else:
                return False
        else:
            return False

    def has_assessor_mode(self,user):
        status_without_assessor = ['with_approver','approved','declined','draft']
        if self.processing_status in status_without_assessor:
            return False
        else:
            if self.assigned_officer:
                if self.assigned_officer == user:
                    return self.__assessor_group() in user.proposalassessorgroup_set.all()
                else:
                    return False
            else:
                return self.__assessor_group() in user.proposalassessorgroup_set.all()

    def log_user_action(self, action, request):
        return ProposalUserAction.log_action(self, action, request.user)

    def submit(self,request,viewset):
        from commercialoperator.components.proposals.utils import save_proponent_data
        with transaction.atomic():
            #import ipdb; ipdb.set_trace()
            if self.can_user_edit:
                # Save the data first
                save_proponent_data(self,request,viewset)
                # Check if the special fields have been completed
                missing_fields = self.__check_proposal_filled_out()
                if missing_fields:
                    error_text = 'The proposal has these missing fields, {}'.format(','.join(missing_fields))
                    raise exceptions.ProposalMissingFields(detail=error_text)
                self.submitter = request.user
                #self.lodgement_date = datetime.datetime.strptime(timezone.now().strftime('%Y-%m-%d'),'%Y-%m-%d').date()
                self.lodgement_date = timezone.now()
                if (self.amendment_requests):
                    qs = self.amendment_requests.filter(status = "requested")
                    if (qs):
                        for q in qs:
                            q.status = 'amended'
                            q.save()

                # Create a log entry for the proposal
                self.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(self.id),request)
                # Create a log entry for the organisation
                #self.applicant.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(self.id),request)
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_LODGE_APPLICATION.format(self.id),request)

                #import ipdb; ipdb.set_trace()
                ret1 = send_submit_email_notification(request, self)
                ret2 = send_external_submit_email_notification(request, self)

                #import ipdb; ipdb.set_trace()
                #self.save_form_tabs(request)
                if ret1 and ret2:
                    self.processing_status = 'with_assessor'
                    self.customer_status = 'with_assessor'
                    self.documents.all().update(can_delete=False)
                    self.save()
                else:
                    raise ValidationError('An error occurred while submitting proposal (Submit email notifications failed)')
                #Create assessor checklist with the current assessor_list type questions
                #Assessment instance already exits then skip.
                try:
                    assessor_assessment=ProposalAssessment.objects.get(proposal=self,referral_group=None, referral_assessment=False)
                except ProposalAssessment.DoesNotExist:
                    assessor_assessment=ProposalAssessment.objects.create(proposal=self,referral_group=None, referral_assessment=False)
                    checklist=ChecklistQuestion.objects.filter(list_type='assessor_list', obsolete=False)
                    for chk in checklist:
                        try:
                            chk_instance=ProposalAssessmentAnswer.objects.get(question=chk, assessment=assessor_assessment)
                        except ProposalAssessmentAnswer.DoesNotExist:
                            chk_instance=ProposalAssessmentAnswer.objects.create(question=chk, assessment=assessor_assessment)

            else:
                raise ValidationError('You can\'t edit this proposal at this moment')

    #TODO: remove this function as it is not used anywhere.
    def save_form_tabs(self,request):
        #self.applicant_details = ProposalApplicantDetails.objects.create(first_name=request.data['first_name'])
        self.activities_land = ProposalActivitiesLand.objects.create(activities_land=request.data['activities_land'])
        self.activities_marine = ProposalActivitiesMarine.objects.create(activities_marine=request.data['activities_marine'])
        #self.save()

    def save_parks(self,request,parks):
        with transaction.atomic():
            if parks:
                try:
                    current_parks=self.parks.all()
                    if current_parks:
                        #print current_parks
                        for p in current_parks:
                            p.delete()
                    for item in parks:
                        try:
                            park=Park.objects.get(id=item)
                            ProposalPark.objects.create(proposal=self, park=park)
                        except:
                            raise
                except:
                    raise



    def update(self,request,viewset):
        from commercialoperator.components.proposals.utils import save_proponent_data
        with transaction.atomic():
            #import ipdb; ipdb.set_trace()
            if self.can_user_edit:
                # Save the data first
                save_proponent_data(self,request,viewset)
                self.save()
            else:
                raise ValidationError('You can\'t edit this proposal at this moment')


    def send_referral(self,request,referral_email,referral_text):
        with transaction.atomic():
            try:
                if self.processing_status == 'with_assessor' or self.processing_status == 'with_referral':
                    self.processing_status = 'with_referral'
                    self.save()
                    referral = None

                    # Check if the user is in ledger
                    try:
                        #user = EmailUser.objects.get(email__icontains=referral_email)
                        referral_group = ReferralRecipientGroup.objects.get(name__icontains=referral_email)
                    #except EmailUser.DoesNotExist:
                    except ReferralRecipientGroup.DoesNotExist:
                        raise exceptions.ProposalReferralCannotBeSent()
#                        # Validate if it is a deparment user
#                        department_user = get_department_user(referral_email)
#                        if not department_user:
#                            raise ValidationError('The user you want to send the referral to is not a member of the department')
#                        # Check if the user is in ledger or create
#                        #import ipdb; ipdb.set_trace()
#                        email = department_user['email'].lower()
#                        user,created = EmailUser.objects.get_or_create(email=department_user['email'].lower())
#                        if created:
#                            user.first_name = department_user['given_name']
#                            user.last_name = department_user['surname']
#                            user.save()
                    try:
                        #Referral.objects.get(referral=user,proposal=self)
                        Referral.objects.get(referral_group=referral_group,proposal=self)
                        raise ValidationError('A referral has already been sent to this group')
                    except Referral.DoesNotExist:
                        # Create Referral
                        referral = Referral.objects.create(
                            proposal = self,
                            #referral=user,
                            referral_group=referral_group,
                            sent_by=request.user,
                            text=referral_text
                        )
                        #Create assessor checklist with the current assessor_list type questions
                        #Assessment instance already exits then skip.
                        try:
                            referral_assessment=ProposalAssessment.objects.get(proposal=self,referral_group=referral_group, referral_assessment=True, referral=referral)
                        except ProposalAssessment.DoesNotExist:
                            referral_assessment=ProposalAssessment.objects.create(proposal=self,referral_group=referral_group, referral_assessment=True, referral=referral)
                            checklist=ChecklistQuestion.objects.filter(list_type='referral_list', obsolete=False)
                            for chk in checklist:
                                try:
                                    chk_instance=ProposalAssessmentAnswer.objects.get(question=chk, assessment=referral_assessment)
                                except ProposalAssessmentAnswer.DoesNotExist:
                                    chk_instance=ProposalAssessmentAnswer.objects.create(question=chk, assessment=referral_assessment)
                    # Create a log entry for the proposal
                    #self.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.id,'{}({})'.format(user.get_full_name(),user.email)),request)
                    self.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.id,'{}'.format(referral_group.name)),request)
                    # Create a log entry for the organisation
                    #self.applicant.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.id,'{}({})'.format(user.get_full_name(),user.email)),request)
                    applicant_field=getattr(self, self.applicant_field)
                    applicant_field.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.id,'{}'.format(referral_group.name)),request)
                    # send email
                    recipients = referral_group.members_list
                    send_referral_email_notification(referral,recipients,request)
                else:
                    raise exceptions.ProposalReferralCannotBeSent()
            except:
                raise

    def assign_officer(self,request,officer):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not self.can_assess(officer):
                    raise ValidationError('The selected person is not authorised to be assigned to this proposal')
                if self.processing_status == 'with_approver':
                    if officer != self.assigned_approver:
                        self.assigned_approver = officer
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_APPROVER.format(self.id,'{}({})'.format(officer.get_full_name(),officer.email)),request)
                        # Create a log entry for the organisation
                        applicant_field=getattr(self, self.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_APPROVER.format(self.id,'{}({})'.format(officer.get_full_name(),officer.email)),request)
                else:
                    if officer != self.assigned_officer:
                        self.assigned_officer = officer
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_ASSESSOR.format(self.id,'{}({})'.format(officer.get_full_name(),officer.email)),request)
                        # Create a log entry for the organisation
                        applicant_field=getattr(self, self.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_ASSIGN_TO_ASSESSOR.format(self.id,'{}({})'.format(officer.get_full_name(),officer.email)),request)
            except:
                raise

    def assing_approval_level_document(self, request):
        with transaction.atomic():
            try:
                approval_level_document = request.data['approval_level_document']
                if approval_level_document != 'null':
                    try:
                        document = self.documents.get(input_name=str(approval_level_document))
                    except ProposalDocument.DoesNotExist:
                        document = self.documents.get_or_create(input_name=str(approval_level_document), name=str(approval_level_document))[0]
                    document.name = str(approval_level_document)
                    # commenting out below tow lines - we want to retain all past attachments - reversion can use them
                    #if document._file and os.path.isfile(document._file.path):
                    #    os.remove(document._file.path)
                    document._file = approval_level_document
                    document.save()
                    d=ProposalDocument.objects.get(id=document.id)
                    self.approval_level_document = d
                    comment = 'Approval Level Document Added: {}'.format(document.name)
                else:
                    self.approval_level_document = None
                    comment = 'Approval Level Document Deleted: {}'.format(request.data['approval_level_document_name'])
                #self.save()
                self.save(version_comment=comment) # to allow revision to be added to reversion history
                self.log_user_action(ProposalUserAction.ACTION_APPROVAL_LEVEL_DOCUMENT.format(self.id),request)
                # Create a log entry for the organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_APPROVAL_LEVEL_DOCUMENT.format(self.id),request)
                return self
            except:
                raise

    def unassign(self,request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status == 'with_approver':
                    if self.assigned_approver:
                        self.assigned_approver = None
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(ProposalUserAction.ACTION_UNASSIGN_APPROVER.format(self.id),request)
                        # Create a log entry for the organisation
                        applicant_field=getattr(self, self.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_UNASSIGN_APPROVER.format(self.id),request)
                else:
                    if self.assigned_officer:
                        self.assigned_officer = None
                        self.save()
                        # Create a log entry for the proposal
                        self.log_user_action(ProposalUserAction.ACTION_UNASSIGN_ASSESSOR.format(self.id),request)
                        # Create a log entry for the organisation
                        applicant_field=getattr(self, self.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_UNASSIGN_ASSESSOR.format(self.id),request)
            except:
                raise

    def move_to_status(self,request,status, approver_comment):
        if not self.can_assess(request.user):
            raise exceptions.ProposalNotAuthorized()
        if status in ['with_assessor','with_assessor_requirements','with_approver']:
            if self.processing_status == 'with_referral' or self.can_user_edit:
                raise ValidationError('You cannot change the current status at this time')
            if self.processing_status != status:
                if self.processing_status =='with_approver':
                    if approver_comment:
                        self.approver_comment = approver_comment
                        self.save()
                        send_proposal_approver_sendback_email_notification(request, self)
                self.processing_status = status
                self.save()

                # Create a log entry for the proposal
                if self.processing_status == self.PROCESSING_STATUS_WITH_ASSESSOR:
                    self.log_user_action(ProposalUserAction.ACTION_BACK_TO_PROCESSING.format(self.id),request)
                elif self.processing_status == self.PROCESSING_STATUS_WITH_ASSESSOR_REQUIREMENTS:
                    self.log_user_action(ProposalUserAction.ACTION_ENTER_REQUIREMENTS.format(self.id),request)
        else:
            raise ValidationError('The provided status cannot be found.')


    def reissue_approval(self,request,status):
        if not self.processing_status=='approved' :
            raise ValidationError('You cannot change the current status at this time')
        elif self.approval and self.approval.can_reissue:
            if self.__approver_group() in request.user.proposalapprovergroup_set.all():
                #import ipdb; ipdb.set_trace()
                self.processing_status = status
                self.save()
                # Create a log entry for the proposal
                self.log_user_action(ProposalUserAction.ACTION_REISSUE_APPROVAL.format(self.id),request)
            else:
                raise ValidationError('Cannot reissue Approval. User not permitted.')
        else:
            raise ValidationError('Cannot reissue Approval')


    def proposed_decline(self,request,details):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_assessor':
                    raise ValidationError('You cannot propose to decline if it is not with assessor')

                reason = details.get('reason')
                ProposalDeclinedDetails.objects.update_or_create(
                    proposal = self,
                    defaults={'officer': request.user, 'reason': reason, 'cc_email': details.get('cc_email',None)}
                )
                self.proposed_decline_status = True
                approver_comment = ''
                self.move_to_status(request,'with_approver', approver_comment)
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_PROPOSED_DECLINE.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_PROPOSED_DECLINE.format(self.id),request)

                send_approver_decline_email_notification(reason, request, self)
            except:
                raise

    def final_decline(self,request,details):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_approver':
                    raise ValidationError('You cannot decline if it is not with approver')

                proposal_decline, success = ProposalDeclinedDetails.objects.update_or_create(
                    proposal = self,
                    defaults={'officer':request.user,'reason':details.get('reason'),'cc_email':details.get('cc_email',None)}
                )
                self.proposed_decline_status = True
                self.processing_status = 'declined'
                self.customer_status = 'declined'
                self.save()
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_DECLINE.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_DECLINE.format(self.id),request)
                send_proposal_decline_email_notification(self,request, proposal_decline)
            except:
                raise

    def on_hold(self,request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not (self.processing_status == 'with_assessor' or self.processing_status == 'with_referral'):
                    raise ValidationError('You cannot put on hold if it is not with assessor or with referral')

                self.prev_processing_status = self.processing_status
                self.processing_status = self.PROCESSING_STATUS_ONHOLD
                self.save()
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_PUT_ONHOLD.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_PUT_ONHOLD.format(self.id),request)

                #send_approver_decline_email_notification(reason, request, self)
            except:
                raise

    def on_hold_remove(self,request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'on_hold':
                    raise ValidationError('You cannot remove on hold if it is not currently on hold')

                self.processing_status = self.prev_processing_status
                self.prev_processing_status = self.PROCESSING_STATUS_ONHOLD
                self.save()
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_REMOVE_ONHOLD.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_REMOVE_ONHOLD.format(self.id),request)

                #send_approver_decline_email_notification(reason, request, self)
            except:
                raise

    def with_qaofficer(self,request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if not (self.processing_status == 'with_assessor' or self.processing_status == 'with_referral'):
                    raise ValidationError('You cannot send to QA Officer if it is not with assessor or with referral')

                self.prev_processing_status = self.processing_status
                self.processing_status = self.PROCESSING_STATUS_WITH_QA_OFFICER
                self.qaofficer_referral = True
                if self.qaofficer_referrals.exists():
                    qaofficer_referral = self.qaofficer_referrals.first()
                    qaofficer_referral.sent_by = request.user
                    qaofficer_referral.processing_status = 'with_qaofficer'
                else:
                    qaofficer_referral = self.qaofficer_referrals.create(sent_by=request.user)

                qaofficer_referral.save()
                self.save()

                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_WITH_QA_OFFICER.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_WITH_QA_OFFICER.format(self.id),request)

                #send_approver_decline_email_notification(reason, request, self)
                recipients = self.qa_officers()
                send_qaofficer_email_notification(self, recipients, request)

            except:
                raise

    def with_qaofficer_completed(self,request):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_qa_officer':
                    raise ValidationError('You cannot Complete QA Officer Assessment if processing status not currently With Assessor')

                self.processing_status = self.prev_processing_status
                self.prev_processing_status = self.PROCESSING_STATUS_WITH_QA_OFFICER

                qaofficer_referral = self.qaofficer_referrals.first()
                qaofficer_referral.qaofficer = request.user
                qaofficer_referral.qaofficer_group = QAOfficerGroup.objects.get(default=True)
                qaofficer_referral.qaofficer_text = request.data['text']
                qaofficer_referral.processing_status = 'completed'

                qaofficer_referral.save()
                self.assigned_officer = None
                self.save()

                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_QA_OFFICER_COMPLETED.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_QA_OFFICER_COMPLETED.format(self.id),request)

                #send_approver_decline_email_notification(reason, request, self)
                recipients = self.qa_officers()
                send_qaofficer_complete_email_notification(self, recipients, request)
            except:
                raise


    def proposed_approval(self,request,details):
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_assessor_requirements':
                    raise ValidationError('You cannot propose for approval if it is not with assessor for requirements')
                self.proposed_issuance_approval = {
                    'start_date' : details.get('start_date').strftime('%d/%m/%Y'),
                    'expiry_date' : details.get('expiry_date').strftime('%d/%m/%Y'),
                    'details': details.get('details'),
                    'cc_email':details.get('cc_email')
                }
                self.proposed_decline_status = False
                approver_comment = ''
                self.move_to_status(request,'with_approver', approver_comment)
                self.assigned_officer = None
                self.save()
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_PROPOSED_APPROVAL.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_PROPOSED_APPROVAL.format(self.id),request)

                send_approver_approve_email_notification(request, self)
            except:
                raise

    def eclass_approval(self,request,details):
        from commercialoperator.components.approvals.models import Approval
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_approver':
                    raise ValidationError('You cannot issue the approval if it is not with an approver')
                if not self.applicant.organisation.postal_address:
                    raise ValidationError('The applicant needs to have set their postal address before approving this proposal.')

                self.proposed_issuance_approval = {
                    'start_date' : details.get('start_date').strftime('%d/%m/%Y'),
                    'expiry_date' : details.get('expiry_date').strftime('%d/%m/%Y'),
                    'details': details.get('details'),
                    'cc_email':details.get('cc_email')
                }
                self.proposed_decline_status = False
                self.processing_status = 'approved'
                self.customer_status = 'approved'
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_ISSUE_APPROVAL_.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_ISSUE_APPROVAL_.format(self.id),request)

                if self.proposal_type == 'renewal':
                    pass
                else:
                    approval,created = Approval.objects.update_or_create(
                        current_proposal = self,
                        defaults = {
                            #'title' : self.title,
                            #'issue_date' : timezone.now(),
                            'issue_date' : details.get('issue_date'),
                            'expiry_date' : details.get('expiry_date'),
                            'start_date' : details.get('start_date'),
                            'applicant' : self.applicant
                        }
                    )
                self.approval = approval

                #send Proposal approval email with attachment
                #send_proposal_approval_email_notification(self,request)
                self.save(version_comment='Final Approval: {}'.format(self.approval.lodgement_number))
                self.approval.documents.all().update(can_delete=False)

            except:
                raise


    def final_approval(self,request,details):
        from commercialoperator.components.approvals.models import Approval
        with transaction.atomic():
            try:
                if not self.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.processing_status != 'with_approver':
                    raise ValidationError('You cannot issue the approval if it is not with an approver')
                #if not self.applicant.organisation.postal_address:
                if not self.applicant_address:
                    raise ValidationError('The applicant needs to have set their postal address before approving this proposal.')

                self.proposed_issuance_approval = {
                    'start_date' : details.get('start_date').strftime('%d/%m/%Y'),
                    'expiry_date' : details.get('expiry_date').strftime('%d/%m/%Y'),
                    'details': details.get('details'),
                    'cc_email':details.get('cc_email')
                }
                self.proposed_decline_status = False
                self.processing_status = 'approved'
                self.customer_status = 'approved'
                # Log proposal action
                self.log_user_action(ProposalUserAction.ACTION_ISSUE_APPROVAL_.format(self.id),request)
                # Log entry for organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_ISSUE_APPROVAL_.format(self.id),request)

                if self.processing_status == 'approved':
                    # TODO if it is an ammendment proposal then check appropriately
                    #import ipdb; ipdb.set_trace()
                    checking_proposal = self
                    if self.proposal_type == 'renewal':
                        if self.previous_application:
                            previous_approval = self.previous_application.approval
                            approval,created = Approval.objects.update_or_create(
                                current_proposal = checking_proposal,
                                defaults = {
                                    #'activity' : self.activity,
                                    #'region' : self.region,
                                    #'tenure' : self.tenure,
                                    #'title' : self.title,
                                    'issue_date' : timezone.now(),
                                    'expiry_date' : details.get('expiry_date'),
                                    'start_date' : details.get('start_date'),
                                    #'applicant' : self.applicant,
                                    'submitter': self.submitter,
                                    'org_applicant' : self.applicant if isinstance(self.applicant, Organisation) else None,
                                    'proxy_applicant' : self.applicant if isinstance(self.applicant, EmailUser) else None,
                                    'lodgement_number': previous_approval.lodgement_number
                                    #'extracted_fields' = JSONField(blank=True, null=True)
                                }
                            )
                            if created:
                                previous_approval.replaced_by = approval
                                previous_approval.save()

                    elif self.proposal_type == 'amendment':
                        if self.previous_application:
                            previous_approval = self.previous_application.approval
                            approval,created = Approval.objects.update_or_create(
                                current_proposal = checking_proposal,
                                defaults = {
                                    #'activity' : self.activity,
                                    #'region' : self.region,
                                    #'tenure' : self.tenure,
                                    #'title' : self.title,
                                    'issue_date' : timezone.now(),
                                    'expiry_date' : details.get('expiry_date'),
                                    'start_date' : details.get('start_date'),
                                    #'applicant' : self.applicant,
                                    'submitter': self.submitter,
                                    'org_applicant' : self.applicant if isinstance(self.applicant, Organisation) else None,
                                    'proxy_applicant' : self.applicant if isinstance(self.applicant, EmailUser) else None,
                                    'lodgement_number': previous_approval.lodgement_number
                                    #'extracted_fields' = JSONField(blank=True, null=True)
                                }
                            )
                            if created:
                                previous_approval.replaced_by = approval
                                previous_approval.save()
                    else:
                        #import ipdb; ipdb.set_trace()
                        approval,created = Approval.objects.update_or_create(
                            current_proposal = checking_proposal,
                            defaults = {
                                #'activity' : self.activity,
                                #'region' : self.region.name,
                                #'tenure' : self.tenure.name,
                                #'title' : self.title,
                                'issue_date' : timezone.now(),
                                'expiry_date' : details.get('expiry_date'),
                                'start_date' : details.get('start_date'),
                                'submitter': self.submitter,
                                'org_applicant' : self.applicant if isinstance(self.applicant, Organisation) else None,
                                'proxy_applicant' : self.applicant if isinstance(self.applicant, EmailUser) else None,
                                #'extracted_fields' = JSONField(blank=True, null=True)
                            }
                        )
                    # Generate compliances
                    #self.generate_compliances(approval, request)
                    from commercialoperator.components.compliances.models import Compliance, ComplianceUserAction
                    if created:
                        if self.proposal_type == 'amendment':
                            approval_compliances = Compliance.objects.filter(approval= previous_approval, proposal = self.previous_application, processing_status='future')
                            if approval_compliances:
                                for c in approval_compliances:
                                    c.delete()
                        # Log creation
                        # Generate the document
                        approval.generate_doc(request.user)
                        self.generate_compliances(approval, request)
                        # send the doc and log in approval and org
                    else:
                        #approval.replaced_by = request.user
                        approval.replaced_by = self.approval
                        # Generate the document
                        approval.generate_doc(request.user)
                        #Delete the future compliances if Approval is reissued and generate the compliances again.
                        approval_compliances = Compliance.objects.filter(approval= approval, proposal = self, processing_status='future')
                        if approval_compliances:
                            for c in approval_compliances:
                                c.delete()
                        self.generate_compliances(approval, request)
                        # Log proposal action
                        self.log_user_action(ProposalUserAction.ACTION_UPDATE_APPROVAL_.format(self.id),request)
                        # Log entry for organisation
                        applicant_field=getattr(self, self.applicant_field)
                        applicant_field.log_user_action(ProposalUserAction.ACTION_UPDATE_APPROVAL_.format(self.id),request)
                    self.approval = approval
                #send Proposal approval email with attachment
                send_proposal_approval_email_notification(self,request)
                self.save(version_comment='Final Approval: {}'.format(self.approval.lodgement_number))
                self.approval.documents.all().update(can_delete=False)

            except:
                raise



    '''def generate_compliances(self,approval):
        from commercialoperator.components.compliances.models import Compliance
        today = timezone.now().date()
        timedelta = datetime.timedelta

        for req in self.requirements.all():
            if req.recurrence and req.due_date > today:
                current_date = req.due_date
                while current_date < approval.expiry_date:
                    for x in range(req.recurrence_schedule):
                    #Weekly
                        if req.recurrence_pattern == 1:
                            current_date += timedelta(weeks=1)
                    #Monthly
                        elif req.recurrence_pattern == 2:
                            current_date += timedelta(weeks=4)
                            pass
                    #Yearly
                        elif req.recurrence_pattern == 3:
                            current_date += timedelta(days=365)
                    # Create the compliance
                    if current_date <= approval.expiry_date:
                        Compliance.objects.create(
                            proposal=self,
                            due_date=current_date,
                            processing_status='future',
                            approval=approval,
                            requirement=req.requirement,
                        )
                        #TODO add logging for compliance'''


    def generate_compliances(self,approval, request):
        today = timezone.now().date()
        timedelta = datetime.timedelta
        from commercialoperator.components.compliances.models import Compliance, ComplianceUserAction
        #For amendment type of Proposal, check for copied requirements from previous proposal
        if self.proposal_type == 'amendment':
            try:
                for r in self.requirements.filter(copied_from__isnull=False):
                    cs=[]
                    cs=Compliance.objects.filter(requirement=r.copied_from, proposal=self.previous_application, processing_status='due')
                    if cs:
                        if r.is_deleted == True:
                            for c in cs:
                                c.processing_status='discarded'
                                c.customer_status = 'discarded'
                                c.reminder_sent=True
                                c.post_reminder_sent=True
                                c.save()
                        if r.is_deleted == False:
                            for c in cs:
                                c.proposal= self
                                c.approval=approval
                                c.requirement=r
                                c.save()
            except:
                raise
        #requirement_set= self.requirements.filter(copied_from__isnull=True).exclude(is_deleted=True)
        requirement_set= self.requirements.all().exclude(is_deleted=True)

        #for req in self.requirements.all():
        for req in requirement_set:
            try:
                if req.due_date and req.due_date >= today:
                    current_date = req.due_date
                    #create a first Compliance
                    try:
                        compliance= Compliance.objects.get(requirement = req, due_date = current_date)
                    except Compliance.DoesNotExist:
                        compliance =Compliance.objects.create(
                                    proposal=self,
                                    due_date=current_date,
                                    processing_status='future',
                                    approval=approval,
                                    requirement=req,
                        )
                        compliance.log_user_action(ComplianceUserAction.ACTION_CREATE.format(compliance.id),request)
                    if req.recurrence:
                        while current_date < approval.expiry_date:
                            for x in range(req.recurrence_schedule):
                            #Weekly
                                if req.recurrence_pattern == 1:
                                    current_date += timedelta(weeks=1)
                            #Monthly
                                elif req.recurrence_pattern == 2:
                                    current_date += timedelta(weeks=4)
                                    pass
                            #Yearly
                                elif req.recurrence_pattern == 3:
                                    current_date += timedelta(days=365)
                            # Create the compliance
                            if current_date <= approval.expiry_date:
                                try:
                                    compliance= Compliance.objects.get(requirement = req, due_date = current_date)
                                except Compliance.DoesNotExist:
                                    compliance =Compliance.objects.create(
                                                proposal=self,
                                                due_date=current_date,
                                                processing_status='future',
                                                approval=approval,
                                                requirement=req,
                                    )
                                    compliance.log_user_action(ComplianceUserAction.ACTION_CREATE.format(compliance.id),request)
            except:
                raise



    def renew_approval(self,request):
        with transaction.atomic():
            previous_proposal = self
            try:
                proposal=Proposal.objects.get(previous_application = previous_proposal)
                if proposal.customer_status=='with_assessor':
                    raise ValidationError('A renewal for this licence has already been lodged and is awaiting review.')
            except Proposal.DoesNotExist:
                previous_proposal = Proposal.objects.get(id=self.id)
                proposal = clone_proposal_with_status_reset(previous_proposal)
                proposal.proposal_type = 'renewal'
                #proposal.schema = ProposalType.objects.first().schema
                ptype = ProposalType.objects.filter(name=proposal.application_type).latest('version')
                proposal.schema = ptype.schema
                proposal.submitter = request.user
                proposal.previous_application = self
                proposal.proposed_issuance_approval= None
                try:
                    ProposalOtherDetails.objects.get(proposal=proposal)
                except ProposalOtherDetails.DoesNotExist:
                    ProposalOtherDetails.objects.create(proposal=proposal)
                # Create a log entry for the proposal
                proposal.other_details.nominated_start_date=self.approval.expiry_date+ datetime.timedelta(days=1)
                proposal.other_details.save()
                self.log_user_action(ProposalUserAction.ACTION_RENEW_PROPOSAL.format(self.id),request)
                # Create a log entry for the organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_RENEW_PROPOSAL.format(self.id),request)
                #Log entry for approval
                from commercialoperator.components.approvals.models import ApprovalUserAction
                self.approval.log_user_action(ApprovalUserAction.ACTION_RENEW_APPROVAL.format(self.approval.id),request)
                proposal.save(version_comment='New Amendment/Renewal Application created, from origin {}'.format(proposal.previous_application_id))
                #proposal.save()
            return proposal

    def amend_approval(self,request):
        with transaction.atomic():
            previous_proposal = self
            try:
                amend_conditions = {
                'previous_application': previous_proposal,
                'proposal_type': 'amendment'

                }
                proposal=Proposal.objects.get(**amend_conditions)
                if proposal.customer_status=='under_review':
                    raise ValidationError('An amendment for this licence has already been lodged and is awaiting review.')
            except Proposal.DoesNotExist:
                previous_proposal = Proposal.objects.get(id=self.id)
                proposal = clone_proposal_with_status_reset(previous_proposal)
                proposal.proposal_type = 'amendment'
                #proposal.schema = ProposalType.objects.first().schema
                ptype = ProposalType.objects.filter(name=proposal.application_type).latest('version')
                proposal.schema = ptype.schema
                proposal.submitter = request.user
                proposal.previous_application = self
                try:
                    ProposalOtherDetails.objects.get(proposal=proposal)
                except ProposalOtherDetails.DoesNotExist:
                    ProposalOtherDetails.objects.create(proposal=proposal)
                #copy all the requirements from the previous proposal
                #req=self.requirements.all()
                req=self.requirements.all().exclude(is_deleted=True)
                from copy import deepcopy
                if req:
                    for r in req:
                        old_r = deepcopy(r)
                        r.proposal = proposal
                        r.copied_from=old_r
                        r.id = None
                        r.save()
                #copy all the requirement documents from previous proposal
                for requirement in proposal.requirements.all():
                    for requirement_document in RequirementDocument.objects.filter(requirement=requirement.copied_from):
                        requirement_document.requirement = requirement
                        requirement_document.id = None
                        requirement_document._file.name = u'{}/proposals/{}/requirement_documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, requirement_document.name)
                        requirement_document.can_delete = True
                        requirement_document.save()
                            # Create a log entry for the proposal
                self.log_user_action(ProposalUserAction.ACTION_AMEND_PROPOSAL.format(self.id),request)
                # Create a log entry for the organisation
                applicant_field=getattr(self, self.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.ACTION_AMEND_PROPOSAL.format(self.id),request)
                #Log entry for approval
                from commercialoperator.components.approvals.models import ApprovalUserAction
                self.approval.log_user_action(ApprovalUserAction.ACTION_AMEND_APPROVAL.format(self.approval.id),request)
                proposal.save(version_comment='New Amendment/Renewal Application created, from origin {}'.format(proposal.previous_application_id))
                #proposal.save()
            return proposal

class ProposalLogDocument(Document):
    log_entry = models.ForeignKey('ProposalLogEntry',related_name='documents')
    _file = models.FileField(upload_to=update_proposal_comms_log_filename)

    class Meta:
        app_label = 'commercialoperator'

class ProposalLogEntry(CommunicationsLogEntry):
    proposal = models.ForeignKey(Proposal, related_name='comms_logs')

    def __str__(self):
        return '{} - {}'.format(self.reference, self.subject)

    class Meta:
        app_label = 'commercialoperator'

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.proposal.reference
        super(ProposalLogEntry, self).save(**kwargs)

class ProposalOtherDetails(models.Model):
    #activities_land = models.CharField(max_length=24, blank=True, default='')
    # ACCREDITATION_TYPE_CHOICES = (
    #     ('no', 'No'),
    #     ('atap', 'ATAP'),
    #     ('eco_certification', 'Eco Certification'),
    #     ('narta', 'NARTA'),
    # )
    # LICENSE_PERIOD_CHOICES=(
    #     ('2_months','2 months'),
    #     ('1_year','1 Year'),
    #     ('3_year', '3 Years'),
    #     ('5_year', '5 Years'),
    #     ('7_year', '7 Years'),
    #     ('10_year', '10 Years'),
    # )
    LICENCE_PERIOD_CHOICES=(
        ('2_months','2 months'),
        ('1_year','1 Year'),
        ('3_year', '3 Years'),
        ('5_year', '5 Years'),
        ('7_year', '7 Years'),
        ('10_year', '10 Years'),
    )
    #accreditation_type = models.CharField('Accreditation', max_length=40, choices=ACCREDITATION_TYPE_CHOICES,
    #                                   default=ACCREDITATION_TYPE_CHOICES[0][0])
    #accreditation_expiry= models.DateTimeField(blank=True, null=True)
    #accreditation_expiry= models.DateField(blank=True, null=True)

    #preferred_license_period=models.CharField('Preferred license period', max_length=40, choices=LICENSE_PERIOD_CHOICES,default=LICENSE_PERIOD_CHOICES[0][0])
    preferred_licence_period=models.CharField('Preferred licence period', max_length=40, choices=LICENCE_PERIOD_CHOICES, null=True, blank=True)
    #nominated_start_date= models.DateTimeField(blank=True, null=True)
    #insurance_expiry= models.DateTimeField(blank=True, null=True)
    nominated_start_date= models.DateField(blank=True, null=True)
    insurance_expiry= models.DateField(blank=True, null=True)
    other_comments=models.TextField(blank=True)
    mooring = JSONField(default=[''])
    #if credit facilities for payment of fees is required
    credit_fees=models.BooleanField(default=False)
    #if credit/ cash payment docket books are required
    credit_docket_books=models.BooleanField(default=False)
    docket_books_number=models.CharField('Docket books number', max_length=20, blank=True )
    proposal = models.OneToOneField(Proposal, related_name='other_details', null=True)

    class Meta:
        app_label = 'commercialoperator'

    @property
    def proposed_end_date(self):
        end_date=None
        if self.preferred_licence_period and self.nominated_start_date:
            if self.preferred_licence_period=='2_months':
                end_date=self.nominated_start_date + relativedelta(months=+2) - relativedelta(days=1)
            if self.preferred_licence_period=='1_year':
                end_date=self.nominated_start_date + relativedelta(months=+12)- relativedelta(days=1)
            if self.preferred_licence_period=='3_year':
                end_date=self.nominated_start_date + relativedelta(months=+36)- relativedelta(days=1)
            if self.preferred_licence_period=='5_year':
                end_date=self.nominated_start_date + relativedelta(months=+60)- relativedelta(days=1)
            if self.preferred_licence_period=='7_year':
                end_date=self.nominated_start_date + relativedelta(months=+84)- relativedelta(days=1)
            if self.preferred_licence_period=='10_year':
                end_date=self.nominated_start_date + relativedelta(months=+120)- relativedelta(days=1)
        return end_date




class ProposalAccreditation(models.Model):
    #activities_land = models.CharField(max_length=24, blank=True, default='')
    ACCREDITATION_TYPE_CHOICES = (
        ('no', 'No'),
        ('atap', 'ATAP'),
        ('eco_certification', 'Eco Certification'),
        ('narta', 'NARTA'),
        ('other', 'Other')
    )

    accreditation_type = models.CharField('Accreditation', max_length=40, choices=ACCREDITATION_TYPE_CHOICES,
                                       default=ACCREDITATION_TYPE_CHOICES[0][0])
    accreditation_expiry= models.DateField(blank=True, null=True)
    comments=models.TextField(blank=True)
    proposal_other_details = models.ForeignKey(ProposalOtherDetails, related_name='accreditations', null=True)

    def __str__(self):
        return '{} - {}'.format(self.accreditation_type, self.comments)

    class Meta:
        app_label = 'commercialoperator'


class ProposalPark(models.Model):
    park = models.ForeignKey(Park, blank=True, null=True, related_name='proposals')
    proposal = models.ForeignKey(Proposal, blank=True, null=True, related_name='parks')

    def __str__(self):
        return self.park.name

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('park', 'proposal')

    @property
    def land_activities(self):
        qs=self.activities.all()
        categories=ActivityCategory.objects.filter(activity_type='land')
        activities=qs.filter(Q(activity__activity_category__in = categories)& Q(activity__visible=True))
        return activities

    @property
    def marine_activities(self):
        qs=self.activities.all()
        categories=ActivityCategory.objects.filter(activity_type='marine')
        activities=qs.filter(Q(activity__activity_category__in = categories)& Q(activity__visible=True))
        return activities

#To store Park activities related to Proposal T class land parks
class ProposalParkActivity(models.Model):
    proposal_park = models.ForeignKey(ProposalPark, blank=True, null=True, related_name='activities')
    activity = models.ForeignKey(Activity, blank=True, null=True)

    def __str__(self):
        return self.activity.name

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('proposal_park', 'activity')

    @property
    def activity_name(self):
        return self.activity.name


#To store Park access_types related to Proposal T class land parks
class ProposalParkAccess(models.Model):
    proposal_park = models.ForeignKey(ProposalPark, blank=True, null=True, related_name='access_types')
    access_type = models.ForeignKey(AccessType, blank=True, null=True)

    def __str__(self):
        return self.access_type.name

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('proposal_park', 'access_type')

#To store Park zones related to Proposal T class marine parks
class ProposalParkZone(models.Model):
    proposal_park = models.ForeignKey(ProposalPark, blank=True, null=True, related_name='zones')
    zone = models.ForeignKey(Zone, blank=True, null=True, related_name='proposal_zones')
    access_point = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.zone.name

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('zone', 'proposal_park')

class ProposalParkZoneActivity(models.Model):
    park_zone = models.ForeignKey(ProposalParkZone, blank=True, null=True, related_name='park_activities')
    activity = models.ForeignKey(Activity, blank=True, null=True)
    #section=models.ForeignKey(Section, blank=True, null= True)

    def __str__(self):
        return '{} - {}'.format(self.activity.name, self.park_zone.zone.name)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('park_zone', 'activity')

    @property
    def activity_name(self):
        return self.activity.name


class ProposalTrail(models.Model):
    trail = models.ForeignKey(Trail, blank=True, null=True, related_name='proposals')
    proposal = models.ForeignKey(Proposal, blank=True, null=True, related_name='trails')

    def __str__(self):
        return self.trail.name

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('trail', 'proposal')

    # @property
    # def sections(self):
    #     qs=self.activities.all()
    #     categories=ActivityCategory.objects.filter(activity_type='land')
    #     activities=qs.filter(Q(activity__activity_category__in = categories)& Q(activity__visible=True))
    #     return activities

class ProposalTrailSection(models.Model):
    proposal_trail = models.ForeignKey(ProposalTrail, blank=True, null=True, related_name='sections')
    section = models.ForeignKey(Section, blank=True, null=True, related_name='proposal_trails')

    def __str__(self):
        return '{} - {}'.format(self.proposal_trail, self.section.name)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('section', 'proposal_trail')

#TODO: Need to remove this model
# class ProposalTrailActivity(models.Model):
#     proposal_trail = models.ForeignKey(ProposalTrail, blank=True, null=True, related_name='trail_activities')
#     activity = models.ForeignKey(Activity, blank=True, null=True)
#     section=models.ForeignKey(Section, blank=True, null= True)

#     class Meta:
#         app_label = 'commercialoperator'
#         unique_together = ('proposal_trail', 'activity')

class ProposalTrailSectionActivity(models.Model):
    trail_section = models.ForeignKey(ProposalTrailSection, blank=True, null=True, related_name='trail_activities')
    activity = models.ForeignKey(Activity, blank=True, null=True)
    #section=models.ForeignKey(Section, blank=True, null= True)

    def __str__(self):
        return '{} - {}'.format(self.trail_section, self.activity.name)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('trail_section', 'activity')

    @property
    def activity_name(self):
        return self.activity.name

@python_2_unicode_compatible
class Vehicle(models.Model):
    capacity = models.CharField(max_length=200, blank=True)
    rego = models.CharField(max_length=200, blank=True)
    license = models.CharField(max_length=200, blank=True)
    access_type= models.ForeignKey(AccessType,null=True, related_name='vehicles')
    rego_expiry= models.DateField(blank=True, null=True)
    proposal = models.ForeignKey(Proposal, related_name='vehicles')

    def __str__(self):
        return '{} - {}'.format(self.rego, self.access_type)

    class Meta:
        app_label = 'commercialoperator'

    def __str__(self):
        return self.rego


@python_2_unicode_compatible
class Vessel(models.Model):
    nominated_vessel = models.CharField(max_length=200, blank=True)
    spv_no = models.CharField(max_length=200, blank=True)
    hire_rego = models.CharField(max_length=200, blank=True)
    craft_no = models.CharField(max_length=200, blank=True)
    size = models.CharField(max_length=200, blank=True)
    #rego_expiry= models.DateField(blank=True, null=True)
    proposal = models.ForeignKey(Proposal, related_name='vessels')

    def __str__(self):
        return '{} - {}'.format(self.spv_no, self.nominated_vessel)

    class Meta:
        app_label = 'commercialoperator'

    def __str__(self):
        return self.nominated_vessel

class ProposalRequest(models.Model):
    proposal = models.ForeignKey(Proposal, related_name='proposalrequest_set')
    subject = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    officer = models.ForeignKey(EmailUser, null=True)

    def __str__(self):
        return '{} - {}'.format(self.subject, self.text)

    class Meta:
        app_label = 'commercialoperator'

class ComplianceRequest(ProposalRequest):
    REASON_CHOICES = (('outstanding', 'There are currently outstanding returns for the previous licence'),
                      ('other', 'Other'))
    reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])

    class Meta:
        app_label = 'commercialoperator'


class AmendmentReason(models.Model):
    reason = models.CharField('Reason', max_length=125)

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Amendment Reason" # display name in Admin
        verbose_name_plural = "Application Amendment Reasons"

    def __str__(self):
        return self.reason


class AmendmentRequest(ProposalRequest):
    STATUS_CHOICES = (('requested', 'Requested'), ('amended', 'Amended'))
    #REASON_CHOICES = (('insufficient_detail', 'The information provided was insufficient'),
    #                  ('missing_information', 'There was missing information'),
    #                  ('other', 'Other'))
    # try:
    #     # model requires some choices if AmendmentReason does not yet exist or is empty
    #     REASON_CHOICES = list(AmendmentReason.objects.values_list('id', 'reason'))
    #     if not REASON_CHOICES:
    #         REASON_CHOICES = ((0, 'The information provided was insufficient'),
    #                           (1, 'There was missing information'),
    #                           (2, 'Other'))
    # except:
    #     REASON_CHOICES = ((0, 'The information provided was insufficient'),
    #                       (1, 'There was missing information'),
    #                       (2, 'Other'))


    status = models.CharField('Status', max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    #reason = models.CharField('Reason', max_length=30, choices=REASON_CHOICES, default=REASON_CHOICES[0][0])
    reason = models.ForeignKey(AmendmentReason, blank=True, null=True)
    #reason = models.ForeignKey(AmendmentReason)

    class Meta:
        app_label = 'commercialoperator'


    def generate_amendment(self,request):
        with transaction.atomic():
            try:
                if not self.proposal.can_assess(request.user):
                    raise exceptions.ProposalNotAuthorized()
                if self.status == 'requested':
                    proposal = self.proposal
                    if proposal.processing_status != 'draft':
                        proposal.processing_status = 'draft'
                        proposal.customer_status = 'draft'
                        proposal.save()

                    # Create a log entry for the proposal
                    proposal.log_user_action(ProposalUserAction.ACTION_ID_REQUEST_AMENDMENTS,request)
                    # Create a log entry for the organisation
                    applicant_field=getattr(proposal, proposal.applicant_field)
                    applicant_field.log_user_action(ProposalUserAction.ACTION_ID_REQUEST_AMENDMENTS,request)

                    # send email

                    send_amendment_email_notification(self,request, proposal)

                self.save()
            except:
                raise

class Assessment(ProposalRequest):
    STATUS_CHOICES = (('awaiting_assessment', 'Awaiting Assessment'), ('assessed', 'Assessed'),
                      ('assessment_expired', 'Assessment Period Expired'))
    assigned_assessor = models.ForeignKey(EmailUser, blank=True, null=True)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    date_last_reminded = models.DateField(null=True, blank=True)
    #requirements = models.ManyToManyField('Requirement', through='AssessmentRequirement')
    comment = models.TextField(blank=True)
    purpose = models.TextField(blank=True)

    class Meta:
        app_label = 'commercialoperator'

class ProposalDeclinedDetails(models.Model):
    #proposal = models.OneToOneField(Proposal, related_name='declined_details')
    proposal = models.OneToOneField(Proposal)
    officer = models.ForeignKey(EmailUser, null=False)
    reason = models.TextField(blank=True)
    cc_email = models.TextField(null=True)

    class Meta:
        app_label = 'commercialoperator'

class ProposalOnHold(models.Model):
    #proposal = models.OneToOneField(Proposal, related_name='onhold')
    proposal = models.OneToOneField(Proposal)
    officer = models.ForeignKey(EmailUser, null=False)
    comment = models.TextField(blank=True)
    documents = models.ForeignKey(ProposalDocument, blank=True, null=True, related_name='onhold_documents')

    class Meta:
        app_label = 'commercialoperator'


@python_2_unicode_compatible
#class ProposalStandardRequirement(models.Model):
class ProposalStandardRequirement(RevisionedMixin):
    text = models.TextField()
    code = models.CharField(max_length=10, unique=True)
    obsolete = models.BooleanField(default=False)

    def __str__(self):
        return self.code

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Application Standard Requirement"
        verbose_name_plural = "Application Standard Requirements"


class ProposalUserAction(UserAction):
    ACTION_CREATE_CUSTOMER_ = "Create customer {}"
    ACTION_CREATE_PROFILE_ = "Create profile {}"
    ACTION_LODGE_APPLICATION = "Lodge application {}"
    ACTION_ASSIGN_TO_ASSESSOR = "Assign application {} to {} as the assessor"
    ACTION_UNASSIGN_ASSESSOR = "Unassign assessor from application {}"
    ACTION_ASSIGN_TO_APPROVER = "Assign application {} to {} as the approver"
    ACTION_UNASSIGN_APPROVER = "Unassign approver from application {}"
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
    ACTION_DECLINE = "Decline application {}"
    ACTION_ENTER_CONDITIONS = "Enter requirement"
    ACTION_CREATE_CONDITION_ = "Create requirement {}"
    ACTION_ISSUE_APPROVAL_ = "Issue Licence for application {}"
    ACTION_UPDATE_APPROVAL_ = "Update Licence for application {}"
    ACTION_EXPIRED_APPROVAL_ = "Expire Approval for proposal {}"
    ACTION_DISCARD_PROPOSAL = "Discard application {}"
    ACTION_APPROVAL_LEVEL_DOCUMENT = "Assign Approval level document {}"
    #T-Class licence
    ACTION_LINK_PARK = "Link park {} to application {}"
    ACTION_UNLINK_PARK = "Unlink park {} from application {}"
    ACTION_LINK_ACCESS = "Link access {} to park {}"
    ACTION_UNLINK_ACCESS = "Unlink access {} from park {}"
    ACTION_LINK_ACTIVITY = "Link activity {} to park {}"
    ACTION_UNLINK_ACTIVITY = "Unlink activity {} from park {}"
    ACTION_LINK_ACTIVITY_SECTION = "Link activity {} to section {} of trail {}"
    ACTION_UNLINK_ACTIVITY_SECTION = "Unlink activity {} from section {} of trail {}"
    ACTION_LINK_ACTIVITY_ZONE = "Link activity {} to zone {} of park {}"
    ACTION_UNLINK_ACTIVITY_ZONE = "Unlink activity {} from zone {} of park {}"
    ACTION_LINK_TRAIL = "Link trail {} to application {}"
    ACTION_UNLINK_TRAIL = "Unlink trail {} from application {}"
    ACTION_LINK_SECTION = "Link section {} to trail {}"
    ACTION_UNLINK_SECTION = "Unlink section {} from trail {}"
    ACTION_LINK_ZONE = "Link zone {} to park {}"
    ACTION_UNLINK_ZONE = "Unlink zone {} from park {}"
    # Assessors
    ACTION_SAVE_ASSESSMENT_ = "Save assessment {}"
    ACTION_CONCLUDE_ASSESSMENT_ = "Conclude assessment {}"
    ACTION_PROPOSED_APPROVAL = "Application {} has been proposed for approval"
    ACTION_PROPOSED_DECLINE = "Application {} has been proposed for decline"
    # Referrals
    ACTION_SEND_REFERRAL_TO = "Send referral {} for application {} to {}"
    ACTION_RESEND_REFERRAL_TO = "Resend referral {} for application {} to {}"
    ACTION_REMIND_REFERRAL = "Send reminder for referral {} for application {} to {}"
    ACTION_ENTER_REQUIREMENTS = "Enter Requirements for application {}"
    ACTION_BACK_TO_PROCESSING = "Back to processing for application {}"
    RECALL_REFERRAL = "Referral {} for application {} has been recalled"
    CONCLUDE_REFERRAL = "{}: Referral {} for application {} has been concluded by group {}"
    ACTION_REFERRAL_DOCUMENT = "Assign Referral document {}"
    #Approval
    ACTION_REISSUE_APPROVAL = "Reissue licence for application {}"
    ACTION_CANCEL_APPROVAL = "Cancel licence for application {}"
    ACTION_EXTEND_APPROVAL = "Extend licence"
    ACTION_SUSPEND_APPROVAL = "Suspend licence for application {}"
    ACTION_REINSTATE_APPROVAL = "Reinstate licence for application {}"
    ACTION_SURRENDER_APPROVAL = "Surrender licence for application {}"
    ACTION_RENEW_PROPOSAL = "Create Renewal application for application {}"
    ACTION_AMEND_PROPOSAL = "Create Amendment application for application {}"
    #Vehicle
    ACTION_CREATE_VEHICLE = "Create Vehicle {}"
    ACTION_EDIT_VEHICLE = "Edit Vehicle {}"
    #Vessel
    ACTION_CREATE_VESSEL = "Create Vessel {}"
    ACTION_EDIT_VESSEL= "Edit Vessel {}"
    ACTION_PUT_ONHOLD = "Put Application On-hold {}"
    ACTION_REMOVE_ONHOLD = "Remove Application On-hold {}"
    ACTION_WITH_QA_OFFICER = "Send Application QA Officer {}"
    ACTION_QA_OFFICER_COMPLETED = "QA Officer Assessment Completed {}"


    class Meta:
        app_label = 'commercialoperator'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, proposal, action, user):
        return cls.objects.create(
            proposal=proposal,
            who=user,
            what=str(action)
        )

    proposal = models.ForeignKey(Proposal, related_name='action_logs')


class ReferralRecipientGroup(models.Model):
    #site = models.OneToOneField(Site, default='1')
    name = models.CharField(max_length=30, unique=True)
    members = models.ManyToManyField(EmailUser)

    def __str__(self):
        #return 'Referral Recipient Group'
        return self.name

    @property
    def all_members(self):
        all_members = []
        all_members.extend(self.members.all())
        member_ids = [m.id for m in self.members.all()]
        #all_members.extend(EmailUser.objects.filter(is_superuser=True,is_staff=True,is_active=True).exclude(id__in=member_ids))
        return all_members

    @property
    def filtered_members(self):
        return self.members.all()

    @property
    def members_list(self):
            return list(self.members.all().values_list('email', flat=True))

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Referral group"
        verbose_name_plural = "Referral groups"

class QAOfficerGroup(models.Model):
    #site = models.OneToOneField(Site, default='1')
    name = models.CharField(max_length=30, unique=True)
    members = models.ManyToManyField(EmailUser)
    default = models.BooleanField(default=False)

    def __str__(self):
        return 'QA Officer Group'

    @property
    def all_members(self):
        all_members = []
        all_members.extend(self.members.all())
        member_ids = [m.id for m in self.members.all()]
        #all_members.extend(EmailUser.objects.filter(is_superuser=True,is_staff=True,is_active=True).exclude(id__in=member_ids))
        return all_members

    @property
    def filtered_members(self):
        return self.members.all()

    @property
    def members_list(self):
            return list(self.members.all().values_list('email', flat=True))

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "QA group"
        verbose_name_plural = "QA group"


    def _clean(self):
        try:
            default = QAOfficerGroup.objects.get(default=True)
        except ProposalAssessorGroup.DoesNotExist:
            default = None

        if default and self.default:
            raise ValidationError('There can only be one default proposal QA Officer group')

    @property
    def current_proposals(self):
        assessable_states = ['with_qa_officer']
        return Proposal.objects.filter(processing_status__in=assessable_states)


#
#class ReferralRequestUserAction(UserAction):
#    ACTION_LODGE_REQUEST = "Lodge request {}"
#    ACTION_ASSIGN_TO = "Assign to {}"
#    ACTION_UNASSIGN = "Unassign"
#    ACTION_DECLINE_REQUEST = "Decline request"
#    # Assessors
#
#    ACTION_CONCLUDE_REQUEST = "Conclude request {}"
#
#    @classmethod
#    def log_action(cls, request, action, user):
#        return cls.objects.create(
#            request=request,
#            who=user,
#            what=str(action)
#        )
#
#    request = models.ForeignKey(ReferralRequest,related_name='action_logs')
#
#    class Meta:
#        app_label = 'commercialoperator'


#class Referral(models.Model):
class Referral(RevisionedMixin):
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
    sent_by = models.ForeignKey(EmailUser,related_name='commercialoperator_assessor_referrals')
    referral = models.ForeignKey(EmailUser,null=True,blank=True,related_name='commercialoperator_referalls')
    referral_group = models.ForeignKey(ReferralRecipientGroup,null=True,blank=True,related_name='commercialoperator_referral_groups')
    linked = models.BooleanField(default=False)
    sent_from = models.SmallIntegerField(choices=SENT_CHOICES,default=SENT_CHOICES[0][0])
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[0][0])
    text = models.TextField(blank=True) #Assessor text
    referral_text = models.TextField(blank=True)
    document = models.ForeignKey(ReferralDocument, blank=True, null=True, related_name='referral_document')


    class Meta:
        app_label = 'commercialoperator'
        ordering = ('-lodged_on',)

    def __str__(self):
        return 'Application {} - Referral {}'.format(self.proposal.id,self.id)

    # Methods
    @property
    def latest_referrals(self):
        return Referral.objects.filter(sent_by=self.referral, proposal=self.proposal)[:2]

    @property
    def referral_assessment(self):
        qs=self.assessment.filter(referral_assessment=True, referral_group=self.referral_group)
        if qs:
            return qs[0]
        else:
            return None


    @property
    def can_be_completed(self):
        return True
        #Referral cannot be completed until second level referral sent by referral has been completed/recalled
        qs=Referral.objects.filter(sent_by=self.referral, proposal=self.proposal, processing_status='with_referral')
        if qs:
            return False
        else:
            return True

    def can_process(self, user):
        if self.processing_status=='with_referral':
            group =  ReferralRecipientGroup.objects.filter(id=self.referral_group.id)
            #user=request.user
            if group and group[0] in user.referralrecipientgroup_set.all():
                return True
            else:
                return False
        return False


    def recall(self,request):
        with transaction.atomic():
            if not self.proposal.can_assess(request.user):
                raise exceptions.ProposalNotAuthorized()
            self.processing_status = 'recalled'
            self.save()
            # TODO Log proposal action
            self.proposal.log_user_action(ProposalUserAction.RECALL_REFERRAL.format(self.id,self.proposal.id),request)
            # TODO log organisation action
            applicant_field=getattr(self.proposal, self.proposal.applicant_field)
            applicant_field.log_user_action(ProposalUserAction.RECALL_REFERRAL.format(self.id,self.proposal.id),request)

    def remind(self,request):
        with transaction.atomic():
            if not self.proposal.can_assess(request.user):
                raise exceptions.ProposalNotAuthorized()
            # Create a log entry for the proposal
            #self.proposal.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
            self.proposal.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
            # Create a log entry for the organisation
            applicant_field=getattr(self.proposal, self.proposal.applicant_field)
            applicant_field.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
            # send email
            recipients = self.referral_group.members_list
            send_referral_email_notification(self,recipients,request,reminder=True)

    def resend(self,request):
        with transaction.atomic():
            if not self.proposal.can_assess(request.user):
                raise exceptions.ProposalNotAuthorized()
            self.processing_status = 'with_referral'
            self.proposal.processing_status = 'with_referral'
            self.proposal.save()
            self.sent_from = 1
            self.save()
            # Create a log entry for the proposal
            #self.proposal.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
            self.proposal.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
            # Create a log entry for the organisation
            #self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
            applicant_field=getattr(self.proposal, self.proposal.applicant_field)
            applicant_field.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
            # send email
            recipients = self.referral_group.members_list
            send_referral_email_notification(self,recipients,request)

    def complete(self,request):
        with transaction.atomic():
            try:
                #if request.user != self.referral:
                group =  ReferralRecipientGroup.objects.filter(id=self.referral_group.id)
                #print u.referralrecipientgroup_set.all()
                user=request.user
                if group and group[0] not in user.referralrecipientgroup_set.all():
                    raise exceptions.ReferralNotAuthorized()
                #import ipdb; ipdb.set_trace()
                self.processing_status = 'completed'
                self.referral = request.user
                self.referral_text = request.user.get_full_name() + ': ' + request.data.get('referral_comment')
                self.add_referral_document(request)
                self.save()
                # TODO Log proposal action
                #self.proposal.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
                self.proposal.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(request.user.get_full_name(), self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
                # TODO log organisation action
                #self.proposal.applicant.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
                applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                applicant_field.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(request.user.get_full_name(), self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
                send_referral_complete_email_notification(self,request)
            except:
                raise

    def add_referral_document(self, request):
        with transaction.atomic():
            try:
                if request.data.has_key('referral_document'):
                    referral_document = request.data['referral_document']
                    #import ipdb; ipdb.set_trace()
                    if referral_document != 'null':
                        try:
                            document = self.referral_documents.get(input_name=str(referral_document))
                        except ReferralDocument.DoesNotExist:
                            document = self.referral_documents.get_or_create(input_name=str(referral_document), name=str(referral_document))[0]
                        document.name = str(referral_document)
                        # commenting out below tow lines - we want to retain all past attachments - reversion can use them
                        #if document._file and os.path.isfile(document._file.path):
                        #    os.remove(document._file.path)
                        document._file = referral_document
                        document.save()
                        d=ReferralDocument.objects.get(id=document.id)
                        self.referral_document = d
                        comment = 'Referral Document Added: {}'.format(document.name)
                    else:
                        self.referral_document = None
                        #comment = 'Referral Document Deleted: {}'.format(request.data['referral_document_name'])
                        comment = 'Referral Document Deleted'
                    #self.save()
                    self.save(version_comment=comment) # to allow revision to be added to reversion history
                    self.proposal.log_user_action(ProposalUserAction.ACTION_REFERRAL_DOCUMENT.format(self.id),request)
                    # Create a log entry for the organisation
                    applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                    applicant_field.log_user_action(ProposalUserAction.ACTION_REFERRAL_DOCUMENT.format(self.id),request)
                return self
            except:
                raise


    def send_referral(self,request,referral_email,referral_text):
        with transaction.atomic():
            try:
                #import ipdb; ipdb.set_trace()
                if self.proposal.processing_status == 'with_referral':
                    if request.user != self.referral:
                        raise exceptions.ReferralNotAuthorized()
                    if self.sent_from != 1:
                        raise exceptions.ReferralCanNotSend()
                    self.proposal.processing_status = 'with_referral'
                    self.proposal.save()
                    referral = None
                    # Check if the user is in ledger
                    try:
                        user = EmailUser.objects.get(email__icontains=referral_email)
                    except EmailUser.DoesNotExist:
                        # Validate if it is a deparment user
                        department_user = get_department_user(referral_email)
                        if not department_user:
                            raise ValidationError('The user you want to send the referral to is not a member of the department')
                        # Check if the user is in ledger or create

                        user,created = EmailUser.objects.get_or_create(email=department_user['email'].lower())
                        if created:
                            user.first_name = department_user['given_name']
                            user.last_name = department_user['surname']
                            user.save()
                    qs=Referral.objects.filter(sent_by=user, proposal=self.proposal)
                    if qs:
                        raise ValidationError('You cannot send referral to this user')
                    try:
                        Referral.objects.get(referral=user,proposal=self.proposal)
                        raise ValidationError('A referral has already been sent to this user')
                    except Referral.DoesNotExist:
                        # Create Referral
                        referral = Referral.objects.create(
                            proposal = self.proposal,
                            referral=user,
                            sent_by=request.user,
                            sent_from=2,
                            text=referral_text
                        )
                        # try:
                        #     referral_assessment=ProposalAssessment.objects.get(proposal=self,referral_group=referral_group, referral_assessment=True, referral=referral)
                        # except ProposalAssessment.DoesNotExist:
                        #     referral_assessment=ProposalAssessment.objects.create(proposal=self,referral_group=referral_group, referral_assessment=True, referral=referral)
                        #     checklist=ChecklistQuestion.objects.filter(list_type='referral_list', obsolete=False)
                        #     for chk in checklist:
                        #         try:
                        #             chk_instance=ProposalAssessmentAnswer.objects.get(question=chk, assessment=referral_assessment)
                        #         except ProposalAssessmentAnswer.DoesNotExist:
                        #             chk_instance=ProposalAssessmentAnswer.objects.create(question=chk, assessment=referral_assessment)
                    # Create a log entry for the proposal
                    self.proposal.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.proposal.id,'{}({})'.format(user.get_full_name(),user.email)),request)
                    # Create a log entry for the organisation
                    applicant_field=getattr(self.proposal, self.proposal.applicant_field)
                    applicant_field.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.proposal.id,'{}({})'.format(user.get_full_name(),user.email)),request)
                    # send email
                    recipients = self.email_group.members_list
                    send_referral_email_notification(referral,recipients,request)
                else:
                    raise exceptions.ProposalReferralCannotBeSent()
            except:
                raise


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

    # @property
    # def applicant(self):
    #     return self.proposal.applicant.name

    @property
    def applicant(self):
        return self.proposal.applicant

    @property
    def can_be_processed(self):
        return self.processing_status == 'with_referral'

    def can_assess_referral(self,user):
        return self.processing_status == 'with_referral'

class ProposalRequirement(OrderedModel):
    RECURRENCE_PATTERNS = [(1, 'Weekly'), (2, 'Monthly'), (3, 'Yearly')]
    standard_requirement = models.ForeignKey(ProposalStandardRequirement,null=True,blank=True)
    free_requirement = models.TextField(null=True,blank=True)
    standard = models.BooleanField(default=True)
    proposal = models.ForeignKey(Proposal,related_name='requirements')
    due_date = models.DateField(null=True,blank=True)
    recurrence = models.BooleanField(default=False)
    recurrence_pattern = models.SmallIntegerField(choices=RECURRENCE_PATTERNS,default=1)
    recurrence_schedule = models.IntegerField(null=True,blank=True)
    copied_from = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    #To determine if requirement has been added by referral and the group of referral who added it
    #Null if added by an assessor
    referral_group = models.ForeignKey(ReferralRecipientGroup,null=True,blank=True,related_name='requirement_referral_groups')
    #order = models.IntegerField(default=1)

    class Meta:
        app_label = 'commercialoperator'


    @property
    def requirement(self):
        return self.standard_requirement.text if self.standard else self.free_requirement

    def can_referral_edit(self,user):
        if self.proposal.processing_status=='with_referral':
            if self.referral_group:
                group =  ReferralRecipientGroup.objects.filter(id=self.referral_group.id)
                #user=request.user
                if group and group[0] in user.referralrecipientgroup_set.all():
                    return True
                else:
                    return False
        return False

    def add_documents(self, request):
        with transaction.atomic():
            try:
                # save the files
                data = json.loads(request.data.get('data'))
                if not data.get('update'):
                    documents_qs = self.requirement_documents.filter(input_name='requirement_doc', visible=True)
                    documents_qs.delete()
                for idx in range(data['num_files']):
                    _file = request.data.get('file-'+str(idx))
                    document = self.requirement_documents.create(_file=_file, name=_file.name)
                    document.input_name = data['input_name']
                    document.can_delete = True
                    document.save()
                # end save documents
                self.save()
            except:
                raise
        return



@python_2_unicode_compatible
#class ProposalStandardRequirement(models.Model):
class ChecklistQuestion(RevisionedMixin):
    TYPE_CHOICES = (
        ('assessor_list','Assessor Checklist'),
        ('referral_list','Referral Checklist')
    )
    text = models.TextField()
    list_type = models.CharField('Checklist type', max_length=30, choices=TYPE_CHOICES,
                                         default=TYPE_CHOICES[0][0])
    #correct_answer= models.BooleanField(default=False)
    obsolete = models.BooleanField(default=False)

    def __str__(self):
        return self.text

    class Meta:
        app_label = 'commercialoperator'


class ProposalAssessment(RevisionedMixin):
    proposal=models.ForeignKey(Proposal, related_name='assessment')
    completed = models.BooleanField(default=False)
    submitter = models.ForeignKey(EmailUser, blank=True, null=True, related_name='proposal_assessment')
    referral_assessment=models.BooleanField(default=False)
    referral_group = models.ForeignKey(ReferralRecipientGroup,null=True,blank=True,related_name='referral_assessment')
    referral=models.ForeignKey(Referral, related_name='assessment',blank=True, null=True )
    # def __str__(self):
    #     return self.proposal

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('proposal', 'referral_group',)

    @property
    def checklist(self):
        return self.answers.all()

    @property
    def referral_group_name(self):
        if self.referral_group:
            return self.referral_group.name
        else:
            return ''


class ProposalAssessmentAnswer(RevisionedMixin):
    question=models.ForeignKey(ChecklistQuestion, related_name='answers')
    answer = models.NullBooleanField()
    assessment=models.ForeignKey(ProposalAssessment, related_name='answers', null=True, blank=True)

    def __str__(self):
        return self.question.text

    class Meta:
        app_label = 'commercialoperator'
        verbose_name = "Assessment answer"
        verbose_name_plural = "Assessment answers"


class QAOfficerReferral(RevisionedMixin):
    SENT_CHOICES = (
        (1,'Sent From Assessor'),
        (2,'Sent From Referral')
    )
    PROCESSING_STATUS_CHOICES = (
                                 ('with_qaofficer', 'Awaiting'),
                                 ('recalled', 'Recalled'),
                                 ('completed', 'Completed'),
                                 )
    lodged_on = models.DateTimeField(auto_now_add=True)
    proposal = models.ForeignKey(Proposal,related_name='qaofficer_referrals')
    sent_by = models.ForeignKey(EmailUser,related_name='assessor_qaofficer_referrals')
    qaofficer = models.ForeignKey(EmailUser, null=True, blank=True, related_name='qaofficers')
    qaofficer_group = models.ForeignKey(QAOfficerGroup,null=True,blank=True,related_name='qaofficer_groups')
    linked = models.BooleanField(default=False)
    sent_from = models.SmallIntegerField(choices=SENT_CHOICES,default=SENT_CHOICES[0][0])
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[0][0])
    text = models.TextField(blank=True) #Assessor text
    qaofficer_text = models.TextField(blank=True)
    document = models.ForeignKey(QAOfficerDocument, blank=True, null=True, related_name='qaofficer_referral_document')


    class Meta:
        app_label = 'commercialoperator'
        ordering = ('-lodged_on',)

    def __str__(self):
        return 'Application {} - QA Officer referral {}'.format(self.proposal.id,self.id)

    # Methods
    @property
    def latest_qaofficer_referrals(self):
        return QAOfficer.objects.filter(sent_by=self.qaofficer, proposal=self.proposal)[:2]

#    @property
#    def can_be_completed(self):
#        #Referral cannot be completed until second level referral sent by referral has been completed/recalled
#        qs=Referral.objects.filter(sent_by=self.referral, proposal=self.proposal, processing_status='with_referral')
#        if qs:
#            return False
#        else:
#            return True
#
#    def recall(self,request):
#        with transaction.atomic():
#            if not self.proposal.can_assess(request.user):
#                raise exceptions.ProposalNotAuthorized()
#            self.processing_status = 'recalled'
#            self.save()
#            # TODO Log proposal action
#            self.proposal.log_user_action(ProposalUserAction.RECALL_REFERRAL.format(self.id,self.proposal.id),request)
#            # TODO log organisation action
#            self.proposal.applicant.log_user_action(ProposalUserAction.RECALL_REFERRAL.format(self.id,self.proposal.id),request)
#
#    def remind(self,request):
#        with transaction.atomic():
#            if not self.proposal.can_assess(request.user):
#                raise exceptions.ProposalNotAuthorized()
#            # Create a log entry for the proposal
#            #self.proposal.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
#            self.proposal.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#            # Create a log entry for the organisation
#            self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_REMIND_REFERRAL.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#            # send email
#            recipients = self.referral_group.members_list
#            send_referral_email_notification(self,recipients,request,reminder=True)
#
#    def resend(self,request):
#        with transaction.atomic():
#            if not self.proposal.can_assess(request.user):
#                raise exceptions.ProposalNotAuthorized()
#            self.processing_status = 'with_referral'
#            self.proposal.processing_status = 'with_referral'
#            self.proposal.save()
#            self.sent_from = 1
#            self.save()
#            # Create a log entry for the proposal
#            #self.proposal.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
#            self.proposal.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#            # Create a log entry for the organisation
#            #self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
#            self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_RESEND_REFERRAL_TO.format(self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#            # send email
#            recipients = self.referral_group.members_list
#            send_referral_email_notification(self,recipients,request)
#
#    def complete(self,request):
#        with transaction.atomic():
#            try:
#                #if request.user != self.referral:
#                group =  ReferralRecipientGroup.objects.filter(name=self.referral_group)
#                if group and group[0] in u.referralrecipientgroup_set.all():
#                    raise exceptions.ReferralNotAuthorized()
#                self.processing_status = 'completed'
#                self.referral = request.user
#                self.referral_text = request.user.get_full_name() + ': ' + request.data.get('referral_comment')
#                self.add_referral_document(request)
#                self.save()
#                # TODO Log proposal action
#                #self.proposal.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
#                self.proposal.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(request.user.get_full_name(), self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#                # TODO log organisation action
#                #self.proposal.applicant.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(self.id,self.proposal.id,'{}({})'.format(self.referral.get_full_name(),self.referral.email)),request)
#                self.proposal.applicant.log_user_action(ProposalUserAction.CONCLUDE_REFERRAL.format(request.user.get_full_name(), self.id,self.proposal.id,'{}'.format(self.referral_group.name)),request)
#                send_referral_complete_email_notification(self,request)
#            except:
#                raise
#
#    def add_referral_document(self, request):
#        with transaction.atomic():
#            try:
#                referral_document = request.data['referral_document']
#                #import ipdb; ipdb.set_trace()
#                if referral_document != 'null':
#                    try:
#                        document = self.referral_documents.get(input_name=str(referral_document))
#                    except ReferralDocument.DoesNotExist:
#                        document = self.referral_documents.get_or_create(input_name=str(referral_document), name=str(referral_document))[0]
#                    document.name = str(referral_document)
#                    # commenting out below tow lines - we want to retain all past attachments - reversion can use them
#                    #if document._file and os.path.isfile(document._file.path):
#                    #    os.remove(document._file.path)
#                    document._file = referral_document
#                    document.save()
#                    d=ReferralDocument.objects.get(id=document.id)
#                    self.referral_document = d
#                    comment = 'Referral Document Added: {}'.format(document.name)
#                else:
#                    self.referral_document = None
#                    comment = 'Referral Document Deleted: {}'.format(request.data['referral_document_name'])
#                #self.save()
#                self.save(version_comment=comment) # to allow revision to be added to reversion history
#                self.proposal.log_user_action(ProposalUserAction.ACTION_REFERRAL_DOCUMENT.format(self.id),request)
#                # Create a log entry for the organisation
#                self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_REFERRAL_DOCUMENT.format(self.id),request)
#                return self
#            except:
#                raise
#
#
#    def send_referral(self,request,referral_email,referral_text):
#        with transaction.atomic():
#            try:
#                #import ipdb; ipdb.set_trace()
#                if self.proposal.processing_status == 'with_referral':
#                    if request.user != self.referral:
#                        raise exceptions.ReferralNotAuthorized()
#                    if self.sent_from != 1:
#                        raise exceptions.ReferralCanNotSend()
#                    self.proposal.processing_status = 'with_referral'
#                    self.proposal.save()
#                    referral = None
#                    # Check if the user is in ledger
#                    try:
#                        user = EmailUser.objects.get(email__icontains=referral_email)
#                    except EmailUser.DoesNotExist:
#                        # Validate if it is a deparment user
#                        department_user = get_department_user(referral_email)
#                        if not department_user:
#                            raise ValidationError('The user you want to send the referral to is not a member of the department')
#                        # Check if the user is in ledger or create
#
#                        user,created = EmailUser.objects.get_or_create(email=department_user['email'].lower())
#                        if created:
#                            user.first_name = department_user['given_name']
#                            user.last_name = department_user['surname']
#                            user.save()
#                    qs=Referral.objects.filter(sent_by=user, proposal=self.proposal)
#                    if qs:
#                        raise ValidationError('You cannot send referral to this user')
#                    try:
#                        Referral.objects.get(referral=user,proposal=self.proposal)
#                        raise ValidationError('A referral has already been sent to this user')
#                    except Referral.DoesNotExist:
#                        # Create Referral
#                        referral = Referral.objects.create(
#                            proposal = self.proposal,
#                            referral=user,
#                            sent_by=request.user,
#                            sent_from=2,
#                            text=referral_text
#                        )
#                    # Create a log entry for the proposal
#                    self.proposal.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.proposal.id,'{}({})'.format(user.get_full_name(),user.email)),request)
#                    # Create a log entry for the organisation
#                    self.proposal.applicant.log_user_action(ProposalUserAction.ACTION_SEND_REFERRAL_TO.format(referral.id,self.proposal.id,'{}({})'.format(user.get_full_name(),user.email)),request)
#                    # send email
#                    recipients = self.email_group.members_list
#                    send_referral_email_notification(referral,recipients,request)
#                else:
#                    raise exceptions.ProposalReferralCannotBeSent()
#            except:
#                raise


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
        return self.processing_status == 'with_qa_officer'

    def can_asses(self):
        return self.can_be_processed and self.proposal.is_qa_officer()


@receiver(pre_delete, sender=Proposal)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()

def clone_proposal_with_status_reset(proposal):
    """
    To Test:
         from commercialoperator.components.proposals.models import clone_proposal_with_status_reset
         p=Proposal.objects.get(id=57)
         p0=clone_proposal_with_status_reset(p)
    """
    with transaction.atomic():
        try:
            original_proposal = copy.deepcopy(proposal)
            #proposal = duplicate_object(proposal) # clone object and related objects
            proposal=duplicate_tclass(proposal)
            # manually duplicate the comms logs -- hck, not hndled by duplicate object (maybe due to inheritance?)
            # proposal.comms_logs.create(text='cloning proposal reset (original proposal {}, new proposal {})'.format(original_proposal.id, proposal.id))
            # for comms_log in proposal.comms_logs.all():
            #     comms_log.id=None
            #     comms_log.communicationslogentry_ptr_id=None
            #     comms_log.proposal_id=original_proposal.id
            #     comms_log.save()

            # reset some properties
            proposal.customer_status = 'draft'
            proposal.processing_status = 'draft'
            proposal.assessor_data = None
            proposal.comment_data = None

            proposal.lodgement_number = ''
            proposal.lodgement_sequence = 0
            proposal.lodgement_date = None

            proposal.assigned_officer = None
            proposal.assigned_approver = None

            proposal.approval = None
            proposal.approval_level_document = None
            proposal.migrated=False

            proposal.save(no_revision=True)

            #clone_documents(proposal, original_proposal, media_prefix='media')
            _clone_documents(proposal, original_proposal, media_prefix='media')
            return proposal
        except:
            raise

def clone_documents(proposal, original_proposal, media_prefix):
    for proposal_document in ProposalDocument.objects.filter(proposal_id=proposal.id):
        proposal_document._file.name = u'{}/proposals/{}/documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, proposal_document.name)
        proposal_document.can_delete = True
        proposal_document.save()

    for proposal_required_document in ProposalRequiredDocument.objects.filter(proposal_id=proposal.id):
        proposal_required_document._file.name = u'{}/proposals/{}/required_documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, proposal_required_document.name)
        proposal_required_document.can_delete = True
        proposal_required_document.save()

    for referral in proposal.referrals.all():
        for referral_document in ReferralDocument.objects.filter(referral=referral):
            referral_document._file.name = u'{}/proposals/{}/referral/{}'.format(settings.MEDIA_APP_DIR, proposal.id, referral_document.name)
            referral_document.can_delete = True
            referral_document.save()

    for qa_officer_document in QAOfficerDocument.objects.filter(proposal_id=proposal.id):
        qa_officer_document._file.name = u'{}/proposals/{}/qaofficer/{}'.format(settings.MEDIA_APP_DIR, proposal.id, qa_officer_document.name)
        qa_officer_document.can_delete = True
        qa_officer_document.save()

    for onhold_document in OnHoldDocument.objects.filter(proposal_id=proposal.id):
        onhold_document._file.name = u'{}/proposals/{}/on_hold/{}'.format(settings.MEDIA_APP_DIR, proposal.id, onhold_document.name)
        onhold_document.can_delete = True
        onhold_document.save()

    for requirement in proposal.requirements.all():
        for requirement_document in RequirementDocument.objects.filter(requirement=requirement):
            requirement_document._file.name = u'{}/proposals/{}/requirement_documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, requirement_document.name)
            requirement_document.can_delete = True
            requirement_document.save()

    for log_entry_document in ProposalLogDocument.objects.filter(log_entry__proposal_id=proposal.id):
        log_entry_document._file.name = log_entry_document._file.name.replace(str(original_proposal.id), str(proposal.id))
        log_entry_document.can_delete = True
        log_entry_document.save()

    # copy documents on file system and reset can_delete flag
    media_dir = '{}/{}'.format(media_prefix, settings.MEDIA_APP_DIR)
    subprocess.call('cp -pr {0}/proposals/{1} {0}/proposals/{2}'.format(media_dir, original_proposal.id, proposal.id), shell=True)


def _clone_documents(proposal, original_proposal, media_prefix):
    for proposal_document in ProposalDocument.objects.filter(proposal=original_proposal.id):
        proposal_document.proposal = proposal
        proposal_document.id = None
        proposal_document._file.name = u'{}/proposals/{}/documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, proposal_document.name)
        proposal_document.can_delete = True
        proposal_document.save()

    for proposal_required_document in ProposalRequiredDocument.objects.filter(proposal=original_proposal.id):
        proposal_required_document.proposal = proposal
        proposal_required_document.id = None
        proposal_required_document._file.name = u'{}/proposals/{}/required_documents/{}'.format(settings.MEDIA_APP_DIR, proposal.id, proposal_required_document.name)
        proposal_required_document.can_delete = True
        proposal_required_document.save()

    # copy documents on file system and reset can_delete flag
    media_dir = '{}/{}'.format(media_prefix, settings.MEDIA_APP_DIR)
    subprocess.call('cp -pr {0}/proposals/{1} {0}/proposals/{2}'.format(media_dir, original_proposal.id, proposal.id), shell=True)

def duplicate_object(self):
    """
    Duplicate a model instance, making copies of all foreign keys pointing to it.
    There are 3 steps that need to occur in order:

        1.  Enumerate the related child objects and m2m relations, saving in lists/dicts
        2.  Copy the parent object per django docs (doesn't copy relations)
        3a. Copy the child objects, relating to the copied parent object
        3b. Re-create the m2m relations on the copied parent object

    """
    related_objects_to_copy = []
    relations_to_set = {}
    # Iterate through all the fields in the parent object looking for related fields
    for field in self._meta.get_fields():
        if field.name in ['proposal', 'approval']:
            print 'Continuing ...'
            pass
        elif field.one_to_many:
            # One to many fields are backward relationships where many child objects are related to the
            # parent (i.e. SelectedPhrases). Enumerate them and save a list so we can copy them after
            # duplicating our parent object.
            print('Found a one-to-many field: {}'.format(field.name))

            # 'field' is a ManyToOneRel which is not iterable, we need to get the object attribute itself
            related_object_manager = getattr(self, field.name)
            related_objects = list(related_object_manager.all())
            if related_objects:
                print(' - {len(related_objects)} related objects to copy')
                related_objects_to_copy += related_objects

        elif field.many_to_one:
            # In testing so far, these relationships are preserved when the parent object is copied,
            # so they don't need to be copied separately.
            print('Found a many-to-one field: {}'.format(field.name))

        elif field.many_to_many:
            # Many to many fields are relationships where many parent objects can be related to many
            # child objects. Because of this the child objects don't need to be copied when we copy
            # the parent, we just need to re-create the relationship to them on the copied parent.
            print('Found a many-to-many field: {}'.format(field.name))
            related_object_manager = getattr(self, field.name)
            relations = list(related_object_manager.all())
            if relations:
                print(' - {} relations to set'.format(len(relations)))
                relations_to_set[field.name] = relations

    # Duplicate the parent object
    self.pk = None
    self.lodgement_number = ''
    self.save()
    print('Copied parent object {}'.format(str(self)))

    # Copy the one-to-many child objects and relate them to the copied parent
    for related_object in related_objects_to_copy:
        # Iterate through the fields in the related object to find the one that relates to the
        # parent model (I feel like there might be an easier way to get at this).
        for related_object_field in related_object._meta.fields:
            if related_object_field.related_model == self.__class__:
                # If the related_model on this field matches the parent object's class, perform the
                # copy of the child object and set this field to the parent object, creating the
                # new child -> parent relationship.
                related_object.pk = None
                #if related_object_field.name=='approvals':
                #    related_object.lodgement_number = None
                ##if isinstance(related_object, Approval):
                ##    related_object.lodgement_number = ''

                setattr(related_object, related_object_field.name, self)
                print related_object_field
                try:
                    related_object.save()
                except Exception, e:
                    logger.warn(e)
                    #import ipdb; ipdb.set_trace()

                text = str(related_object)
                text = (text[:40] + '..') if len(text) > 40 else text
                print('|- Copied child object {}'.format(text))

    # Set the many-to-many relations on the copied parent
    for field_name, relations in relations_to_set.items():
        # Get the field by name and set the relations, creating the new relationships
        field = getattr(self, field_name)
        field.set(relations)
        text_relations = []
        for relation in relations:
            text_relations.append(str(relation))
        print('|- Set {} many-to-many relations on {} {}'.format(len(relations), field_name, text_relations))

    return self

def duplicate_tclass(p):
    original_proposal=copy.deepcopy(p)
    p.id=None
    p.save()
    print ('new proposal',p)

    for park in original_proposal.parks.all():

        original_park=copy.deepcopy(park)
        park.id=None
        park.proposal=p
        park.save()
        print('new park', park,park.id, original_park, original_park.id, park.proposal)
        for activity in original_park.activities.all():
            activity.id=None
            activity.proposal_park=park
            activity.save()
            print('new activity', activity, activity.id, park)
            #new_activities_list.append(new_ac)
        for access in original_park.access_types.all():
            access.id=None
            access.proposal_park=park
            access.save()
            print('new access', access, park)
            #new_access_list.append(new_ac)
        for zone in original_park.zones.all():
            original_zone=copy.deepcopy(zone)
            zone.id=None
            zone.proposal_park=park
            zone.save()
            print('new zone',zone)
            for acz in original_zone.park_activities.all():
                acz.id=None
                acz.park_zone=zone
                acz.save()
                print('new zone activity', acz, zone)

    for trail in original_proposal.trails.all():
        original_trail=copy.deepcopy(trail)
        trail.id=None
        trail.proposal=p
        trail.save()

        for section in original_trail.sections.all():
            original_section=copy.deepcopy(section)
            section.id=None
            section.proposal_trail=trail
            section.save()
            print('new section', section, trail)
            for act in original_section.trail_activities.all():
                act.id=None
                act.trail_section=section
                act.save()
                print('new trail activity', act, section)

    try:
        other_details=ProposalOtherDetails.objects.get(proposal=original_proposal)
        new_accreditations=[]
        print('proposal:',original_proposal, original_proposal.other_details.id, other_details.id)
        print('accreditations', other_details.accreditations.all())
        for acc in other_details.accreditations.all():
            acc.id=None
            acc.save()
            new_accreditations.append(acc)
        other_details.id=None
        other_details.proposal=p
        other_details.save()
        for new_acc in new_accreditations:
            new_acc.proposal_other_details=other_details
            new_acc.save()
    except ProposalOtherDetails.DoesNotExist:
        other_details=ProposalOtherDetails.objects.create(proposal=p)

    for vehicle in original_proposal.vehicles.all():
        vehicle.id=None
        vehicle.proposal=p
        vehicle.save()
    for vessel in original_proposal.vessels.all():
        vessel.id=None
        vessel.proposal=p
        vessel.save()

    return p



def searchKeyWords(searchWords, searchProposal, searchApproval, searchCompliance, is_internal= True):
    from commercialoperator.utils import search, search_approval, search_compliance
    from commercialoperator.components.approvals.models import Approval
    from commercialoperator.components.compliances.models import Compliance
    qs = []
    if is_internal:
        proposal_list = Proposal.objects.filter(application_type__name='T Class').exclude(processing_status__in=['discarded','draft'])
        approval_list = Approval.objects.all().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
        compliance_list = Compliance.objects.all()
    if searchWords:
        if searchProposal:
            for p in proposal_list:
                #if p.data:
                if p.search_data:
                    try:
                        #results = search(p.data[0], searchWords)
                        results = search(p.search_data, searchWords)
                        final_results = {}
                        if results:
                            for r in results:
                                for key, value in r.iteritems():
                                    final_results.update({'key': key, 'value': value})
                            res = {
                                'number': p.lodgement_number,
                                'id': p.id,
                                'type': 'Proposal',
                                'applicant': p.applicant,
                                'text': final_results,
                                }
                            qs.append(res)
                    except:
                        raise
        if searchApproval:
            for a in approval_list:
                try:
                    results = search_approval(a, searchWords)
                    qs.extend(results)
                except:
                    raise
        if searchCompliance:
            for c in compliance_list:
                try:
                    results = search_compliance(c, searchWords)
                    qs.extend(results)
                except:
                    raise
    return qs

def search_reference(reference_number):
    from commercialoperator.components.approvals.models import Approval
    from commercialoperator.components.compliances.models import Compliance
    proposal_list = Proposal.objects.all().exclude(processing_status__in=['discarded'])
    approval_list = Approval.objects.all().order_by('lodgement_number', '-issue_date').distinct('lodgement_number')
    compliance_list = Compliance.objects.all().exclude(processing_status__in=['future'])
    record = {}
    try:
        result = proposal_list.get(lodgement_number = reference_number)
        record = {  'id': result.id,
                    'type': 'proposal' }
    except Proposal.DoesNotExist:
        try:
            result = approval_list.get(lodgement_number = reference_number)
            record = {  'id': result.id,
                        'type': 'approval' }
        except Approval.DoesNotExist:
            try:
                for c in compliance_list:
                    if c.reference == reference_number:
                        record = {  'id': c.id,
                                    'type': 'compliance' }
            except:
                raise ValidationError('Record with provided reference number does not exist')
    if record:
        return record
    else:
        raise ValidationError('Record with provided reference number does not exist')

from ckeditor.fields import RichTextField
class HelpPage(models.Model):
    HELP_TEXT_EXTERNAL = 1
    HELP_TEXT_INTERNAL = 2
    HELP_TYPE_CHOICES = (
        (HELP_TEXT_EXTERNAL, 'External'),
        (HELP_TEXT_INTERNAL, 'Internal'),
    )

    application_type = models.ForeignKey(ApplicationType)
    content = RichTextField()
    description = models.CharField(max_length=256, blank=True, null=True)
    help_type = models.SmallIntegerField('Help Type', choices=HELP_TYPE_CHOICES, default=HELP_TEXT_EXTERNAL)
    version = models.SmallIntegerField(default=1, blank=False, null=False)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('application_type', 'help_type', 'version')

def check_migrate_approval(data):
    '''
    check if all submitters/org_applicants exist
    '''
    from commercialoperator.components.approvals.models import Approval
    org_applicant = None
    proxy_applicant = None
    submitter=None
    try:
        #import ipdb; ipdb.set_trace()

        if data['submitter']:
            submitter = EmailUser.objects.get(email__icontains=data['submitter'])
            if data['org_applicant']:
                #org_applicant = Organisation.objects.get(organisation__name=data['org_applicant'])
                org_applicant = Organisation.objects.get(organisation__abn=data['org_applicant'])
        else:
            ValidationError('Licence holder is required')
    except:
        raise ValidationError('Licence holder is required')

def migrate_approval(data, not_found):
    from commercialoperator.components.approvals.models import Approval
    org_applicant = None
    proxy_applicant = None
    submitter=None
    try:
        #import ipdb; ipdb.set_trace()

        if data['submitter']:
            try:
                submitter = EmailUser.objects.get(email__icontains=data['submitter'])
            except:
                submitter = EmailUser.objects.create(email=data['submitter'], password = '')
            if data['abn']:
                #org_applicant = Organisation.objects.get(organisation__name=data['org_applicant'])
                org_applicant = Organisation.objects.get(organisation__abn=data['abn'])
        else:
            #ValidationError('Licence holder is required')
            logger.error('Licence holder is required: submitter {}, abn {}'.format(data['submitter'], data['abn']))
            not_found.append({'submitter': data['submitter'], 'abn': data['abn']})
            return None
    except Exception, e:
        #raise ValidationError('Licence holder is required: \n{}'.format(e))
        logger.error('Licence holder is required: submitter {}, abn {}'.format(data['submitter'], data['abn']))
        not_found.append({'submitter': data['submitter'], 'abn': data['abn']})
        return None

    application_type=ApplicationType.objects.get(name=data['application_type'])
    application_name = application_type.name
    # Get most recent versions of the Proposal Types
    qs_proposal_type = ProposalType.objects.all().order_by('name', '-version').distinct('name')
    proposal_type = qs_proposal_type.get(name=application_name)
    proposal= Proposal.objects.create( # Dummy 'T Class' proposal
                    application_type=application_type,
                    submitter=submitter,
                    org_applicant=org_applicant,
                    schema=proposal_type.schema
                )
    approval = Approval.objects.create(
                    issue_date=data['issue_date'],
                    expiry_date=data['expiry_date'],
                    start_date=data['start_date'],
                    org_applicant=org_applicant,
                    submitter= submitter,
                    current_proposal=proposal
                )
    proposal.approval= approval
    proposal.processing_status='approved'
    proposal.customer_status='approved'
    proposal.migrated=True
    approval.migrated=True
    other_details = ProposalOtherDetails.objects.create(proposal=proposal)
    proposal.save()
    approval.save()
    return approval

def create_migration_data(filename, verify=False, app_type='T Class'):
    def get_dates(data, row):
        try:
            #import ipdb; ipdb.set_trace()
            if data['start_date']:
                start_date = datetime.datetime.strptime(data['start_date'], '%d-%b-%y').date() # '05-Feb-89'
            else:
                start_date = None

            if data['issue_date']:
                issue_date = datetime.datetime.strptime(data['issue_date'], '%d-%b-%y').date()
            else:
                issue_date = None

            if data['expiry_date']:
                expiry_date = datetime.datetime.strptime(data['expiry_date'], '%d-%b-%y').date()

            if not (start_date and issue_date):
                start_date = datetime.date.today()
                issue_date = datetime.date.today()
            elif not start_date:
                start_date = issue_date
            elif not issue_date:
                issue_date = start_date

        except Exception, e:
            logger.error('Error in Dates: {}'.format(data))
            raise

        data.update({'start_date': start_date})
        data.update({'issue_date': start_date})
        data.update({'expiry_date': expiry_date})

        return data


    try:
        '''
        Example csv
        org_applicant, submitter, start_date, issue_date, expiry_date, application_type
        'Test Org1', 'prerana.andure@dbca.wa.gov.au', '4/07/2019', '4/07/2019', '10/07/2019', 'T Class'

        To test:
            from commercialoperator.components.proposals.models import create_migration_data
            create_migration_data('commercialoperator/utils/csv/approvals.csv')
        '''
        data={}
        not_found=[]
        no_expiry=[]
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, delimiter=str(','))
            header = next(reader) # skip header
            for row in reader:
                #import ipdb; ipdb.set_trace()
                data.update({'abn': row[0].translate(None, string.whitespace)})
                data.update({'submitter': row[1].strip()})
                data.update({'start_date': row[2].strip()})
                data.update({'issue_date': row[3].strip()})
                data.update({'expiry_date': row[4].strip()})
                data.update({'application_type': row[5].strip()})
                data.update({'submitter2': row[6].strip()})
                data.update({'submitter3': row[7].strip()})
                data.update({'submitter4': row[8].strip()})
                data.update({'submitter_full_str': row[9].strip()})

                if data['expiry_date']:
                    get_dates(data, row)
                    if row[5].strip()[0] == 'T':
                        application_type = 'T Class'
                    elif row[5].strip()[0] == 'E':
                        application_type = 'E Class'
                    else:
                        logger.error('Unknown Application Type: {}'.format(row[5].strip()))

                    data.update({'application_type': application_type})
                    #print data

                    if application_type == app_type:
                        if verify:
                            approval=check_migrate_approval(data)
                        else:
                            approval=migrate_approval(data, not_found)
                        #print data
                        print '{} - {}'.format(approval, data['submitter'])
                        print
                else:
                    no_expiry.append(data['submitter'])

        print 'Not Found: {}'.format(not_found)
        print 'No Expiry: {}'.format(no_expiry)
    except Exception, e:
        print data
        print e


def create_organisation(data, count, debug=False):

    #import ipdb; ipdb.set_trace()
    #print 'Data: {}'.format(data)
    #user = None
    try:
        user, created = EmailUser.objects.get_or_create(
            email__icontains=data['email1'],
            defaults={
                'first_name': data['first_name'],
                'last_name': data['last_name'],
                'phone_number': data['phone_number1'],
                'mobile_number': data['mobile_number'],
            },
        )
    except Exception, e:
        print data['email1']
        import ipdb; ipdb.set_trace()

    if debug:
        print 'User: {}'.format(user)


    abn_existing = []
    abn_new = []
    process = True
    try:
        ledger_organisation.objects.get(abn=data['abn'])
        abn_existing.append(data['abn'])
        print '{}, Existing ABN: {}'.format(count, data['abn'])
        process = False
    except Exception, e:
        print '{}, Add ABN: {}'.format(count, data['abn'])
        #import ipdb; ipdb.set_trace()

    if process:
        try:
            #print 'Country: {}'.format(data['country'])
            country=Country.objects.get(printable_name__icontains=data['country'])
            oa, created = OrganisationAddress.objects.get_or_create(
                line1=data['address_line1'],
                locality=data['suburb'],
                postcode=data['postcode'] if data['postcode'] else '0000',
                defaults={
                    'line2': data['address_line2'],
                    'line3': data['address_line3'],
                    'state': data['state'],
                    'country': country.code,
                }
            )
        except:
            print 'Country 2: {}'.format(data['country'])
            import ipdb; ipdb.set_trace()
            raise
        if debug:
            print 'Org Address: {}'.format(oa)

        try:
            lo, created = ledger_organisation.objects.get_or_create(
                abn=data['abn'],
                defaults={
                    'name': data['licencee'],
                    'postal_address': oa,
                    'billing_address': oa,
                    'trading_name': data['trading_name']
                }
            )
            if created:
                abn_new.append(data['abn'])
            else:
                print '******** ERROR ********* abn already exists {}'.format(data['abn'])

        except Exception, e:
            print 'ABN: {}'.format(data['abn'])
            import ipdb; ipdb.set_trace()
            raise

        if debug:
            print 'Ledger Org: {}'.format(lo)

        #import ipdb; ipdb.set_trace()
        try:
            org, created = Organisation.objects.get_or_create(organisation=lo)
        except Exception, e:
            print 'Org: {}'.format(org)
            import ipdb; ipdb.set_trace()
            raise

        if debug:
            print 'Organisation: {}'.format(org)

        try:
            delegate, created = UserDelegation.objects.get_or_create(organisation=org, user=user)
        except Exception, e:
            print 'Delegate Creation Failed: {}'.format(user)
            import ipdb; ipdb.set_trace()
            raise

        if debug:
            print 'Delegate: {}'.format(delegate)

        try:
            oc, created = OrganisationContact.objects.get_or_create(
                organisation=org,
                email=user.email,
                defaults={
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'mobile_number': user.mobile_number if data['mobile_number'] else '',
                    'user_status': 'active',
                    'user_role': 'organisation_admin',
                    'is_admin': True
                }
            )
        except Exception, e:
            print 'Org Contact: {}'.format(user)
            import ipdb; ipdb.set_trace()
            raise

        if debug:
            print 'Org Contact: {}'.format(oc)

        #return abn_new, abn_existing

    return abn_new, abn_existing

def create_organisation_data(filename, verify=False):
    #import ipdb; ipdb.set_trace()
    def get_start_date(data, row):
        try:
            expiry_date = datetime.datetime.strptime(data['expiry_date'], '%d-%b-%y').date() # '05-Feb-89'
        except Exception, e:
            data.update({'start_date': None})
            data.update({'issue_date': None})
            data.update({'expiry_date': None})
            #logger.error('Expiry Date: {}'.format(data['expiry_date']))
            #logger.error('Data: {}'.format(data))
            #raise
            return

        term = data['term'].split() # '3 YEAR'

        #import ipdb; ipdb.set_trace()
        if 'YEAR' in term[1]:
            start_date = expiry_date - relativedelta(years=int(term[0]))
        if 'MONTH' in term[1]:
            start_date = expiry_date - relativedelta(months=int(term[0]))
        else:
            start_date = datetime.date.today()

        data.update({'start_date': start_date})
        data.update({'issue_date': start_date})
        data.update({'expiry_date': expiry_date})

    data={}
    abn_existing = []
    abn_new = []
    count = 1
    try:
        '''
        Example csv
            address, town/city, state (WA), postcode, org_name, abn, trading_name, first_name, last_name, email, phone_number
            123 Something Road, Perth, WA, 6100, Import Test Org 3, 615503, DDD_03, john, Doe_1, john.doe_1@dbca.wa.gov.au, 08 555 5555

            File No:Licence No:Expiry Date:Term:Trading Name:Licensee:ABN:Title:First Name:Surname:Other Contact:Address 1:Address 2:Address 3:Suburb:State:Country:Post:Telephone1:Telephone2:Mobile:Insurance Expiry:Survey Cert:Name:SPV:ATAP Expiry:Eco Cert Expiry:Vessels:Vehicles:Email1:Email2:Email3:Email4
            2018/001899-1:HQ70324:28-Feb-21:3 YEAR:4 U We Do:4 U We Do Pty Ltd::MR:Petrus:Grobler::Po Box 2483:::ESPERANCE:WA:AUSTRALIA:6450:458021841:::23-Jun-18::::30-Jun-18::0:7:groblerp@gmail.com:::
        To test:
            from commercialoperator.components.proposals.models import create_organisation_data
            create_migration_data('commercialoperator/utils/csv/orgs.csv')
        '''
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, delimiter=str(':'))
            header = next(reader) # skip header
            for row in reader:
                #import ipdb; ipdb.set_trace()
                data.update({'file_no': row[0].translate(None, string.whitespace)})
                data.update({'licence_no': row[1].translate(None, string.whitespace)})
                data.update({'expiry_date': row[2].strip()})
                data.update({'term': row[3].strip()})

                get_start_date(data, row)

                data.update({'trading_name': row[4].strip()})
                data.update({'licencee': row[5].strip()})
                data.update({'abn': row[6].translate(None, string.whitespace)})
                data.update({'title': row[7].strip()})
                data.update({'first_name': row[8].strip().capitalize()})
                data.update({'last_name': row[9].strip().capitalize()})
                data.update({'other_contact': row[10].strip()})
                data.update({'address_line1': row[11].strip()})
                data.update({'address_line2': row[12].strip()})
                data.update({'address_line3': row[13].strip()})
                data.update({'suburb': row[14].strip().capitalize()})
                data.update({'state': row[15].strip()})

                country = ' '.join([i.lower().capitalize() for i in row[16].strip().split()])
                if country == 'A':
                    country = 'Australia'
                data.update({'country': country})

                data.update({'postcode': row[17].translate(None, string.whitespace)})
                data.update({'phone_number1': row[18].translate(None, b' -()')})
                data.update({'phone_number2': row[19].translate(None, b' -()')})
                data.update({'mobile_number': row[20].translate(None, b' -()')})

                data.update({'email1': row[29].strip()})
                data.update({'email2': row[30].strip()})
                data.update({'email3': row[31].strip()})
                data.update({'email4': row[32].strip()})
                #import ipdb; ipdb.set_trace()

                #print data

                new, existing = create_organisation(data, count)
                count += 1
                abn_new = new + abn_new
                abn_existing = existing + abn_existing
                #if data['expiry_date']:
                #    organisation=create_organisation(data)
                #else:
                #    logger.warn('No Expiry Date: {}'.format(data))
                #print organisation

        print 'New: {}, Existing: {}'.format(len(abn_new), len(abn_existing))
        print 'New: {}'.format(abn_new)
        print 'Existing: {}'.format(abn_existing)


    except:
        logger.info('Main {}'.format(data))
        raise




import reversion
reversion.register(Referral, follow=['referral_documents', 'assessment'])
reversion.register(ReferralDocument, follow=['referral_document'])

#reversion.register(Proposal, follow=['documents', 'onhold_documents','required_documents','qaofficer_documents','comms_logs','other_details', 'parks', 'trails', 'vehicles', 'vessels', 'proposalrequest_set','proposaldeclineddetails', 'proposalonhold', 'requirements', 'referrals', 'qaofficer_referrals', 'compliances', 'referrals', 'approvals', 'park_entries', 'assessment', 'bookings', 'application_fees'])
reversion.register(Proposal, follow=['documents', 'onhold_documents','required_documents','qaofficer_documents','comms_logs','other_details', 'parks', 'trails', 'vehicles', 'vessels', 'proposalrequest_set','proposaldeclineddetails', 'proposalonhold', 'requirements', 'referrals', 'qaofficer_referrals', 'compliances', 'referrals', 'approvals', 'park_entries', 'assessment'])
reversion.register(ProposalDocument, follow=['onhold_documents'])
reversion.register(OnHoldDocument)
reversion.register(ProposalRequest)
reversion.register(ProposalRequiredDocument)
reversion.register(ProposalApplicantDetails)
reversion.register(ProposalActivitiesLand)
reversion.register(ProposalActivitiesMarine)
reversion.register(ProposalOtherDetails, follow=['accreditations'])

reversion.register(ProposalLogEntry, follow=['documents',])
reversion.register(ProposalLogDocument)

#reversion.register(Park, follow=['proposals',])
reversion.register(ProposalPark, follow=['activities','access_types', 'zones'])
reversion.register(ProposalParkAccess)

#reversion.register(AccessType, follow=['proposals','proposalparkaccess_set', 'vehicles'])

#reversion.register(Activity, follow=['proposalparkactivity_set','proposalparkzoneactivity_set', 'proposaltrailsectionactivity_set'])
reversion.register(ProposalParkActivity)

reversion.register(ProposalParkZone, follow=['park_activities'])
reversion.register(ProposalParkZoneActivity)
reversion.register(ParkEntry)

reversion.register(ProposalTrail, follow=['sections'])
reversion.register(Vehicle)
reversion.register(Vessel)
reversion.register(ProposalUserAction)

reversion.register(ProposalTrailSection, follow=['trail_activities'])

reversion.register(ProposalTrailSectionActivity)
reversion.register(AmendmentReason, follow=['amendmentrequest_set'])
reversion.register(AmendmentRequest)
reversion.register(Assessment)
reversion.register(ProposalDeclinedDetails)
reversion.register(ProposalOnHold)
reversion.register(ProposalStandardRequirement, follow=['proposalrequirement_set'])
reversion.register(ProposalRequirement, follow=['compliance_requirement'])
reversion.register(ReferralRecipientGroup, follow=['commercialoperator_referral_groups', 'referral_assessment'])
reversion.register(QAOfficerGroup, follow=['qaofficer_groups'])
reversion.register(QAOfficerReferral)
reversion.register(QAOfficerDocument, follow=['qaofficer_referral_document'])
reversion.register(ProposalAccreditation)
reversion.register(HelpPage)
reversion.register(ChecklistQuestion, follow=['answers'])
reversion.register(ProposalAssessment, follow=['answers'])
reversion.register(ProposalAssessmentAnswer)


