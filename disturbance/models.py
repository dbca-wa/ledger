from __future__ import unicode_literals

from django.db import models
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import EmailUser 


class Organisation(models.Model):
    organisation = models.ForeignKey(ledger_organisation)
    # TODO: business logic related to delegate changes.
    delegates = models.ManyToManyField(EmailUser, blank=True, through='UserDelegation', related_name='disturbance_organisations')
    pin_one = models.BigIntegerField(blank=True)
    pin_two = models.BigIntegerField(blank=True)

    @staticmethod
    def existance(abn):
        try:
            l_org = ledger_organisation.objects.get(abn=abn)
        except ledger_organisation.DoesNotExist:
            return False
        if l_org:
            try:
                Organisation.objects.get(organisation=l_org)
            except Organisation.DoesNotExist:
                return False
        return True

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

