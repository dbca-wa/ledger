from __future__ import unicode_literals

from django.db import models

from ledger.accounts.models import RevisionedMixin
from ledger.licence.models import LicenceType


class Condition(RevisionedMixin):
    text = models.TextField()


class WildlifeLicenceType(LicenceType):
    default_conditions = models.ManyToManyField(Condition, blank=True)
    identification_required = models.BooleanField(default=False)
