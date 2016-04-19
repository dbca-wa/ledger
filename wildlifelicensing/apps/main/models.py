from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from ledger.accounts.models import RevisionedMixin, EmailUser, Document
from ledger.licence.models import LicenceType


@python_2_unicode_compatible
class Condition(RevisionedMixin):
    text = models.TextField()
    code = models.CharField(max_length=10, unique=True)
    one_off = models.BooleanField(default=False)

    def __str__(self):
        return self.code


class WildlifeLicenceType(LicenceType):
    identification_required = models.BooleanField(default=False)
    default_conditions = models.ManyToManyField(Condition, through='DefaultCondition', blank=True)


class DefaultCondition(models.Model):
    condition = models.ForeignKey(Condition)
    wildlife_licence_type = models.ForeignKey(WildlifeLicenceType)
    order = models.IntegerField()

    class Meta:
        unique_together = ('condition', 'wildlife_licence_type', 'order')


class AbstractLogEntry(models.Model):
    user = models.ForeignKey(EmailUser, null=False, blank=False)
    text = models.TextField(blank=True)
    document = models.ForeignKey(Document, null=True, blank=False)
    created = models.DateField(auto_now_add=True, null=False, blank=False)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class AssessorDepartment(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    members = models.ManyToManyField(EmailUser)
    suggested_conditions = models.ManyToManyField(Condition, blank=True)

    def __str__(self):
        return self.name
