
from __future__ import unicode_literals

import json
import datetime
from django.db import models,transaction
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields.jsonb import JSONField
from django.utils import timezone
from django.contrib.sites.models import Site
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from ledger.accounts.models import Organisation as ledger_organisation
from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.licence.models import  Licence
from wildlifecompliance import exceptions
from wildlifecompliance.components.organisations.models import Organisation
from wildlifecompliance.components.main.models import CommunicationsLogEntry, Region, UserAction, Document

class Return(models.Model):
    PROCESSING_STATUS_CHOICES = (('due', 'Due'), 
                                 ('future', 'Future'), 
                                 ('with_assessor', 'With Assessor'),
                                 ('approved', 'Approved'),
                                 )

    application = models.ForeignKey('wildlifecompliance.Application',related_name='returns')
    licence = models.ForeignKey('wildlifecompliance.WildlifeLicence',related_name='returns')
    due_date = models.DateField()
    processing_status = models.CharField(choices=PROCESSING_STATUS_CHOICES,max_length=20)
    assigned_to = models.ForeignKey(EmailUser,related_name='wildlifecompliance_return_assignments',null=True,blank=True)

    class Meta:
        app_label = 'wildlifecompliance'

    @property
    def regions(self):
        return self.application.regions_list

    @property
    def activity(self):
        return self.application.activity

    @property
    def title(self):
        return self.application.title

    @property
    def holder(self):
        return self.application.applicant


