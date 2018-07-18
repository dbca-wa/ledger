from __future__ import unicode_literals

from django.db import models, transaction
from django.contrib.sites.models import Site
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields.jsonb import JSONField
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import EmailUser, Document, RevisionedMixin
from disturbance.components.main.models import UserAction,CommunicationsLogEntry
from disturbance.components.organisations.utils import random_generator
from disturbance.components.organisations.emails import (
                        send_organisation_request_accept_email_notification,
                        send_organisation_link_email_notification,
                        send_organisation_unlink_email_notification,
                        send_org_access_group_request_accept_email_notification,
            )

@python_2_unicode_compatible
class Organisation(models.Model):
    organisation = models.ForeignKey(ledger_organisation)
    # TODO: business logic related to delegate changes.
    delegates = models.ManyToManyField(EmailUser, blank=True, through='UserDelegation', related_name='disturbance_organisations')
    pin_one = models.CharField(max_length=50,blank=True)
    pin_two = models.CharField(max_length=50,blank=True)

    class Meta:
        app_label = 'disturbance'

    def __str__(self):
        return str(self.organisation)

    def log_user_action(self, action, request):
        return OrganisationAction.log_action(self, action, request.user)

    def validate_pins(self,pin1,pin2,request):
        val = self.pin_one == pin1 and self.pin_two == pin2
        if val:
            self.link_user(request.user,request)
        return val
    
    def link_user(self,user,request):
        with transaction.atomic():
            try:
                UserDelegation.objects.get(organisation=self,user=user)
                raise ValidationError('This user has already been linked to {}'.format(str(self.organisation)))
            except UserDelegation.DoesNotExist:
                delegate = UserDelegation.objects.create(organisation=self,user=user)
            # Create contact person
            OrganisationContact.objects.create(
                organisation = self,
                first_name = user.first_name,
                last_name = user.last_name,
                mobile_number = user.mobile_number,
                phone_number = user.phone_number,
                fax_number = user.fax_number,
                email = user.email
            
            )
            # log linking
            self.log_user_action(OrganisationAction.ACTION_LINK.format('{} {}({})'.format(delegate.user.first_name,delegate.user.last_name,delegate.user.email)),request)
            # send email
            send_organisation_link_email_notification(user,request.user,self,request)

    def unlink_user(self,user,request):
        with transaction.atomic():
            try:
                delegate = UserDelegation.objects.get(organisation=self,user=user)
            except UserDelegation.DoesNotExist:
                raise ValidationError('This user is not a member of {}'.format(str(self.organisation)))
            # delete contact person
            try:
                '''OrganisationContact.objects.get(
                    organisation = self,
                    email = delegate.user.email
                
                ).delete()'''
                org_contact = OrganisationContact.objects.get(organisation = self, email = delegate.user.email)
                if OrganisationContact.objects.filter(organisation=self).count()>1:
                    org_contact.delete()
                else:
                    raise ValidationError('You cannot unlink the last Organisation user')
            except OrganisationContact.DoesNotExist:
                pass
            # delete delegate
            delegate.delete()
            # log linking
            self.log_user_action(OrganisationAction.ACTION_UNLINK.format('{} {}({})'.format(delegate.user.first_name,delegate.user.last_name,delegate.user.email)),request)
            # send email
            send_organisation_unlink_email_notification(user,request.user,self,request)

    def update_organisation(self, request):
        # log organisation details updated (eg ../internal/organisations/access/2) - incorrect - this is for OrganisationRequesti not Organisation
        # should be ../internal/organisations/1
        with transaction.atomic():
            self.log_user_action(OrganisationAction.ACTION_UPDATE_ORGANISATION, request)

    def update_address(self, request):
        self.log_user_action(OrganisationAction.ACTION_UPDATE_ADDRESS, request)

    def update_contacts(self, request):
        try:
            contact = self.contact.last()
            self.log_user_action(OrganisationAction.ACTION_UPDATE_CONTACTS.format('{} {}({})'.format(contact.first_name, contact.last_name, contact.email)), request)
        except:
            pass

    def generate_pins(self):
        self.pin_one = self._generate_pin()
        self.pin_two = self._generate_pin()
        self.save()

    def _generate_pin(self):
        return random_generator()

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
                    org = Organisation.objects.get(organisation=l_org)
                except Organisation.DoesNotExist:
                    exists = False
            if exists:
                return {'exists': exists, 'id': org.id,'first_five':org.first_five}
            return {'exists': exists }
            
        except:
            raise

    @property
    def name(self):
        return self.organisation.name

    @property
    def abn(self):
        return self.organisation.abn

    @property
    def address(self):
        return self.organisation.postal_address

    @property
    def phone_number(self):
        return self.organisation.phone_number

    @property
    def email(self):
        return self.organisation.email

    @property
    def first_five(self):
        return ','.join([user.get_full_name() for user in self.delegates.all()[:5]])

@python_2_unicode_compatible
class OrganisationContact(models.Model):
    organisation = models.ForeignKey(Organisation, related_name='contacts')
    email = models.EmailField(blank=False)
    first_name = models.CharField(max_length=128, blank=False, verbose_name='Given name(s)')
    last_name = models.CharField(max_length=128, blank=False)
    phone_number = models.CharField(max_length=50, null=True, blank=True,
                                    verbose_name="phone number", help_text='')
    mobile_number = models.CharField(max_length=50, null=True, blank=True,
                                     verbose_name="mobile number", help_text='')
    fax_number = models.CharField(max_length=50, null=True, blank=True,
                                  verbose_name="fax number", help_text='')

    class Meta:
        app_label = 'disturbance'
        unique_together = (('organisation','email'),)

    def __str__(self):
        return '{} {}'.format(self.last_name,self.first_name)

class UserDelegation(models.Model):
    organisation = models.ForeignKey(Organisation)
    user = models.ForeignKey(EmailUser)

    class Meta:
        unique_together = (('organisation','user'),)
        app_label = 'disturbance'


class OrganisationAction(UserAction):
    ACTION_REQUEST_APPROVED = "Organisation Request {} Approved"
    ACTION_LINK = "Linked {}"
    ACTION_UNLINK = "Unlinked {}"
    ACTION_CONTACT_ADDED = "Added new contact {}"
    ACTION_CONTACT_REMOVED = "Removed contact {}"
    ACTION_ORGANISATIONAL_DETAILS_SAVED_NOT_CHANGED = "Details saved without changes"
    ACTION_ORGANISATIONAL_DETAILS_SAVED_CHANGED = "Details saved with the following changes: \n{}"
    ACTION_ORGANISATIONAL_ADDRESS_DETAILS_SAVED_NOT_CHANGED = "Address Details saved without changes"
    ACTION_ORGANISATIONAL_ADDRESS_DETAILS_SAVED_CHANGED = "Addres Details saved with folowing changes: \n{}"

    ACTION_UPDATE_ORGANISATION = "Updated organisation name"
    ACTION_UPDATE_ADDRESS = "Updated address"
    ACTION_UPDATE_CONTACTS = "Updated contacts"

    @classmethod
    def log_action(cls, organisation, action, user):
        return cls.objects.create(
            organisation=organisation,
            who=user,
            what=str(action)
        )

    organisation = models.ForeignKey(Organisation,related_name='action_logs')

    class Meta:
        app_label = 'disturbance'

def update_organisation_comms_log_filename(instance, filename):
    return 'organisations/{}/communications/{}/{}'.format(instance.log_entry.organisation.id,instance.id,filename)


class OrganisationLogDocument(Document):
    log_entry = models.ForeignKey('OrganisationLogEntry',related_name='documents')
    _file = models.FileField(upload_to=update_organisation_comms_log_filename)

    class Meta:
        app_label = 'disturbance'

    
class OrganisationLogEntry(CommunicationsLogEntry):
    organisation = models.ForeignKey(Organisation, related_name='comms_logs')

    def save(self, **kwargs):
        # save the request id if the reference not provided
        if not self.reference:
            self.reference = self.organisation.id
        super(OrganisationLogEntry, self).save(**kwargs)

    class Meta:
        app_label = 'disturbance'


class OrganisationRequest(models.Model):
    STATUS_CHOICES = (
        ('with_assessor','With Assessor'),
        ('approved','Approved'),
        ('declined','Declined')
    )
    name = models.CharField(max_length=128, unique=True)
    abn = models.CharField(max_length=50, null=True, blank=True, verbose_name='ABN')
    requester = models.ForeignKey(EmailUser)
    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True, related_name='org_request_assignee')
    identification = models.FileField(upload_to='organisation/requests/%Y/%m/%d', null=True, blank=True)
    status = models.CharField(max_length=100,choices=STATUS_CHOICES, default="with_assessor")
    lodgement_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'disturbance'

    def accept(self, request):
        with transaction.atomic():
            self.status = 'approved'
            self.save()
            self.log_user_action(OrganisationRequestUserAction.ACTION_CONCLUDE_REQUEST.format(self.id),request)
            # Continue with remaining logic
            self.__accept(request)

    def __accept(self,request):
        # Check if orgsanisation exists in ledger
        ledger_org = None
        try:
            ledger_org = ledger_organisation.objects.get(abn=self.abn) 
        except ledger_organisation.DoesNotExist:
            ledger_org = ledger_organisation.objects.create(name=self.name,abn=self.abn)
        # Create Organisation in disturbance
        org = Organisation.objects.create(organisation=ledger_org)
        # Link requester to organisation
        delegate = UserDelegation.objects.create(user=self.requester,organisation=org)
        # log who approved the request
        org.log_user_action(OrganisationAction.ACTION_REQUEST_APPROVED.format(self.id),request)
        # log who created the link
        org.log_user_action(OrganisationAction.ACTION_LINK.format('{} {}({})'.format(delegate.user.first_name,delegate.user.last_name,delegate.user.email)),request)
        # Create contact person
        OrganisationContact.objects.create(
            organisation = org,
            first_name = self.requester.first_name,
            last_name = self.requester.last_name,
            mobile_number = self.requester.mobile_number,
            phone_number = self.requester.phone_number,
            fax_number = self.requester.fax_number,
            email = self.requester.email
        
        )
        # send email to requester
        send_organisation_request_accept_email_notification(self, org, request)

    def send_org_access_group_request_notification(self,request):
        # user submits a new organisation request
        # send email to organisation access group
        org_access_recipients = [i.email for i in OrganisationAccessGroup.objects.last().all_members]
        send_org_access_group_request_accept_email_notification(self, request, org_access_recipients)

    def assign_to(self, user,request):
        with transaction.atomic():
            self.assigned_officer = user
            self.save()
            self.log_user_action(OrganisationRequestUserAction.ACTION_ASSIGN_TO.format(user.get_full_name()),request)

    def unassign(self,request):
        with transaction.atomic():
            self.assigned_officer = None 
            self.save()
            self.log_user_action(OrganisationRequestUserAction.ACTION_UNASSIGN,request)

    def decline(self, reason, request):
        with transaction.atomic():
            self.status = 'declined'
            self.save()
            OrganisationRequestDeclinedDetails.objects.create(
                officer = request.user,
                reason = reason,
                request = self
            )
            self.log_user_action(OrganisationRequestUserAction.ACTION_DECLINE_REQUEST,request)

    def log_user_action(self, action, request):
        return OrganisationRequestUserAction.log_action(self, action, request.user)

class OrganisationAccessGroup(models.Model):
    site = models.OneToOneField(Site, default='1') 
    members = models.ManyToManyField(EmailUser)

    def __str__(self):
        return 'Organisation Access Group'

    @property
    def all_members(self):
        all_members = []
        all_members.extend(self.members.all())
        member_ids = [m.id for m in self.members.all()]
        #all_members.extend(EmailUser.objects.filter(is_superuser=True,is_staff=True,is_active=True).exclude(id__in=member_ids))
        return all_members

    class Meta:
        app_label = 'disturbance'
        
class OrganisationRequestUserAction(UserAction):
    ACTION_LODGE_REQUEST = "Lodge request {}"
    ACTION_ASSIGN_TO = "Assign to {}"
    ACTION_UNASSIGN = "Unassign"
    ACTION_DECLINE_REQUEST = "Decline request"
    # Assessors

    ACTION_CONCLUDE_REQUEST = "Conclude request {}"

    @classmethod
    def log_action(cls, request, action, user):
        return cls.objects.create(
            request=request,
            who=user,
            what=str(action)
        )

    request = models.ForeignKey(OrganisationRequest,related_name='action_logs')

    class Meta:
        app_label = 'disturbance'


class OrganisationRequestDeclinedDetails(models.Model):
    request = models.ForeignKey(OrganisationRequest)
    officer = models.ForeignKey(EmailUser, null=False)
    reason = models.TextField(blank=True)

    class Meta:
        app_label = 'disturbance'

def update_organisation_request_comms_log_filename(instance, filename):
    return 'organisation_requests/{}/communications/{}/{}'.format(instance.log_entry.request.id,instance.id,filename)


class OrganisationRequestLogDocument(Document):
    log_entry = models.ForeignKey('OrganisationRequestLogEntry',related_name='documents')
    _file = models.FileField(upload_to=update_organisation_request_comms_log_filename)

    class Meta:
        app_label = 'disturbance'

class OrganisationRequestLogEntry(CommunicationsLogEntry):
    request = models.ForeignKey(OrganisationRequest, related_name='comms_logs')

    def save(self, **kwargs):
        # save the request id if the reference not provided
        if not self.reference:
            self.reference = self.request.id
        super(OrganisationRequestLogEntry, self).save(**kwargs)

    class Meta:
        app_label = 'disturbance'
