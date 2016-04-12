from __future__ import unicode_literals

from django.db import models

from ledger.accounts.models import RevisionedMixin, EmailUser, Document
from ledger.licence.models import LicenceType


class Condition(RevisionedMixin):
    text = models.TextField()


class WildlifeLicenceType(LicenceType):
    default_conditions = models.ManyToManyField(Condition, blank=True)
    identification_required = models.BooleanField(default=False)


class AbstractLogEntry(models.Model):
    user = models.ForeignKey(EmailUser, null=False, blank=False)
    text = models.TextField(blank=True)
    document = models.ForeignKey(Document, null=True, blank=False)
    created = models.DateField(auto_now_add=True, null=False, blank=False)

    class Meta:
        abstract = True
