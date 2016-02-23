from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from dpaw_utils.models import ActiveMixin, AuditMixin
from addressbook.models import Address


@python_2_unicode_compatible
class CustomerRole(ActiveMixin, AuditMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    organisation_name = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        if self.organisation_name:
            return '{} ({})'.format(self.user, self.organisation_name)
        return '{}'.format(self.user)


@python_2_unicode_compatible
class WildlifeLicenceType(ActiveMixin, AuditMixin):
    name = models.CharField(max_length=256)
    code = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    replaced_by = models.ForeignKey(
        'self', on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class WildlifeLicence(ActiveMixin, AuditMixin):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('granted', 'Granted'),
        ('refused', 'Refused'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired')
    )

    customer_role = models.ForeignKey(CustomerRole, on_delete=models.PROTECT)
    licence_type = models.ForeignKey(
        WildlifeLicenceType, on_delete=models.PROTECT)
    address = models.ForeignKey(Address, on_delete=models.PROTECT)
    status = models.CharField(
        max_length=64, choices=STATUS_CHOICES, default='submitted')
    licence_no = models.CharField(
        max_length=64, unique=True, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    expire_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.customer_role, self.licence_type, self.status)
