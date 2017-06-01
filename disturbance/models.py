from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.sites.models import Site
from taggit.managers import TaggableManager
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import EmailUser 
from disturbance.fields import CommaSeparatedField

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
        ('with_assessor','With Assessor'),
        ('approved','Approved'),
        ('declined','Declined')
    )
    name = models.CharField(max_length=128, unique=True)
    abn = models.CharField(max_length=50, null=True, blank=True, verbose_name='ABN')
    requester = models.ForeignKey(EmailUser)
    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True, related_name='org_request_assignee')
    identification = models.FileField(upload_to='uploads/%Y/%m/%d', null=True, blank=True)
    status = models.CharField(max_length=100,choices=STATUS_CHOICES)

class ProposalType(models.Model):
    schema = JSONField()
    activities = TaggableManager(verbose_name="Activities",help_text="A comma-separated list of activities.") 
    site = models.OneToOneField(Site) 
