from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.postgres.fields import ArrayField

from dpaw_utils.models import ActiveMixin

from ledger.accounts.models import Address, RevisionedMixin


@python_2_unicode_compatible
class LicenceType(RevisionedMixin, ActiveMixin):
    name = models.CharField(max_length=256)
    code = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    replaced_by = models.ForeignKey(
        'self', on_delete=models.PROTECT, blank=True, null=True)
    keywords = ArrayField(models.CharField(max_length=50), blank=True, default=[])

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Licence(RevisionedMixin, ActiveMixin):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('granted', 'Granted'),
        ('refused', 'Refused'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired')
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    licence_type = models.ForeignKey(LicenceType, on_delete=models.PROTECT)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='submitted')
    licence_no = models.CharField(max_length=64, unique=True, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    expire_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return '{} {}'.format(self.licence_type, self.status)
