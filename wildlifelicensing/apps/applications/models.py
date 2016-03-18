from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField

from ledger.licence.models import LicenceType


class Application(models.Model):
    STATES = (('draft', 'Draft'), ('lodged', 'Lodged'))
#    licence_type = models.ForeignKey(LicenceType)
#    user = models.ForeignKey(EmailUser)
    state = models.CharField('Application State', max_length=20, choices=STATES)
    data = JSONField()
