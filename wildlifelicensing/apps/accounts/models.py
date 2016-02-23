from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from addressbook.models import Address
from django.utils.encoding import python_2_unicode_compatible

from wildlifelicensing.apps.main.models import Document


@python_2_unicode_compatible
class Customer(models.Model):
    TITLE_CHOICES = (
        ('Mr', 'Mr'),
        ('Miss', 'Miss'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr')
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=False, blank=False, on_delete=models.PROTECT)
    title = models.CharField(max_length=100, choices=TITLE_CHOICES, blank=False, default=TITLE_CHOICES[0][0],
                             verbose_name='title', help_text="")
    dob = models.DateField(auto_now=False, auto_now_add=False, null=False, blank=False,
                           verbose_name="date of birth", help_text='')
    phone_number = models.CharField(max_length=50, null=True, blank=True,
                                    verbose_name="phone number", help_text='')
    mobile_number = models.CharField(max_length=50, null=True, blank=True,
                                     verbose_name="mobile number", help_text='')
    fax_number = models.CharField(max_length=50, null=True, blank=True,
                                  verbose_name="fax number", help_text='')
    organisation = models.CharField(max_length=300, null=True, blank=True,
                                    verbose_name="organisation", help_text='organisation, institution or company')

    residential_address = models.ForeignKey(Address, null=False, blank=False, related_name='+')
    postal_address = models.ForeignKey(Address, null=True, blank=True, related_name='+')
    billing_address = models.ForeignKey(Address, null=True, blank=True, related_name='+')

    documents = models.ManyToManyField(Document)

    def __str__(self):
        if self.organisation:
            return '{} ({})'.format(self.user, self.organisation)
        return '{}'.format(self.user)

    class Meta:
        db_table = 'wl_accounts_customer'
