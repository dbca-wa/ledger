from __future__ import unicode_literals

from django.db import models
from rollcall.models import EmailUser
from addressbook.models import Address
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Persona(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name='Persona Name',
                            help_text='Persona Name')
    email = models.EmailField(null=True, blank=True, verbose_name='Email', help_text='Email')
    user = models.ForeignKey(EmailUser, null=False, blank=False)
    address = models.ForeignKey(Address, null=True, blank=True)

    def __str__(self):
        return self.name if self.name else self.email

    @property
    def email(self):
        return self.email or self.user.email
