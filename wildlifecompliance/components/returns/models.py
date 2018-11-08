
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
from wildlifecompliance.components.returns.utils_schema import Schema, create_return_template_workbook
from wildlifecompliance.components.organisations.models import Organisation
from wildlifecompliance.components.applications.models import ApplicationCondition,Application
from wildlifecompliance.components.main.models import CommunicationsLogEntry, Region, UserAction, Document


class ReturnType(models.Model):
    Name=models.TextField(null=True,blank=True,max_length=200)
    data_descriptor = JSONField()

    class Meta:
        app_label = 'wildlifecompliance'

    @property
    def resources(self):
        return self.data_descriptor.get('resources', [])


class Return(models.Model):
    PROCESSING_STATUS_CHOICES = (('due', 'Due'), 
                                 ('future', 'Future'), 
                                 ('with_assessor', 'With Assessor'),
                                 ('approved', 'Approved'),
                                 )
    CUSTOMER_STATUS_CHOICES = (('due', 'Due'),
                                 ('future', 'Future'),
                                 ('with_assessor', 'Under Review'),
                                 ('approved', 'Approved'),
                                 ('discarded', 'Discarded'),
                                 )
    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    application = models.ForeignKey(Application,related_name='returns')
    licence = models.ForeignKey('wildlifecompliance.WildlifeLicence',related_name='returns')
    due_date = models.DateField()
    text = models.TextField(blank=True)
    processing_status = models.CharField(choices=PROCESSING_STATUS_CHOICES,max_length=20)
    customer_status = models.CharField(choices=CUSTOMER_STATUS_CHOICES,max_length=20, default=CUSTOMER_STATUS_CHOICES[1][0])
    assigned_to = models.ForeignKey(EmailUser,related_name='wildlifecompliance_return_assignments',null=True,blank=True)
    condition = models.ForeignKey(ApplicationCondition, blank=True, null=True, related_name='returns_condition', on_delete=models.SET_NULL)
    lodgement_date = models.DateTimeField(blank=True, null=True)
    submitter = models.ForeignKey(EmailUser, blank=True, null=True, related_name='disturbance_compliances')
    reminder_sent = models.BooleanField(default=False)
    post_reminder_sent = models.BooleanField(default=False)
    return_type=models.ForeignKey(ReturnType,null=True)

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

    @property
    def resources(self):
        return self.return_type.data_descriptor.get('resources', [])

    @property
    def headers(self):
        for resource in self.return_type.resources:
            resource_name = resource.get('name')
            schema = Schema(resource.get('schema'))
            headers = []
            for f in schema.fields:
                header = {
                    "title": f.name,
                    "required": f.required
                }
                if f.is_species:
                    header["species"] = f.species_type
                headers.append(header)
        return headers




