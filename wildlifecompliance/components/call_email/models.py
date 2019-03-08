from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields.jsonb import JSONField
from django.db.models import Max
from ledger.accounts.models import EmailUser
from ledger.licence.models import LicenceType
from wildlifecompliance.components.organisations.models import Organisation
from wildlifecompliance.components.applications.models import Application
from wildlifecompliance.components.main.models import CommunicationsLogEntry,\
    UserAction, Document

class Classification(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        app_label = 'wildlifecompliance'

    def __str__(self):
        return '{}'.format(self.name)


class CallEmail(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('open_followup', 'Open (follow-up)'),
        ('open_inspection', 'Open (Inspection)'),
        ('open_case', 'Open (Case)'),
        ('closed', 'Closed')
    )

    #classification = models.CharField(max_length=30) # this should be a FK to Admin enum list
    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        default=STATUS_CHOICES[0][0])
    classification = models.ForeignKey(Classification, related_name='calls')


    schema = JSONField(default=list)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'Call/Email'
        verbose_name_plural = 'Calls/Emails'

    def __str__(self):
        return self.status



