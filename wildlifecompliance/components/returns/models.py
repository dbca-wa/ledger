
from __future__ import unicode_literals

import json
import datetime
from preserialize.serialize import serialize
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
from wildlifecompliance.components.returns.email import send_external_submit_email_notification



class ReturnType(models.Model):
    Name=models.TextField(null=True,blank=True,max_length=200)
    data_descriptor = JSONField()

    class Meta:
        app_label = 'wildlifecompliance'

    @property
    def resources(self):
        return self.data_descriptor.get('resources', [])

    def get_resource_by_name(self, name):
        for resource in self.resources:
            if resource.get('name') == name:
                return resource
        return None

    def get_schema_by_name(self, name):
        resource = self.get_resource_by_name(name)
        return resource.get('schema', {}) if resource else None


class Return(models.Model):
    PROCESSING_STATUS_CHOICES = (('due', 'Due'), 
                                 ('overdue','Overdue'),
                                 ('draft','Draft'),
                                 ('future', 'Future'), 
                                 ('with_curator', 'With Curator'),
                                 ('accepted', 'Accepted'),
                                 )
    CUSTOMER_STATUS_CHOICES = (('due', 'Due'),
                                 ('overdue','Overdue'),
                                 ('draft','Draft'),
                                 ('future', 'Future'),
                                 ('under_review', 'Under Review'),
                                 ('accepted', 'Accepted'),
                                 
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
    nil_return = models.BooleanField(default=False)
    comments = models.TextField(blank=True, null=True)

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
    def table(self):
        tables = []
        for resource in self.return_type.resources:
            resource_name = resource.get('name')
            schema = Schema(resource.get('schema'))
            headers = []
            for f in schema.fields:
                # print(type(f.name))
                header = {
                    "title": f.name,
                    "required": f.required
                }
                if f.is_species:
                    header["species"] = f.species_type
                headers.append(header)
            table = {
                'name': resource_name,
                'title': resource.get('title', resource.get('name')),
                'headers': headers,
                'data': None
            }
            try:
                return_table = self.returntable_set.get(name=resource_name)
                rows = [return_row.data for return_row in return_table.returnrow_set.all()]
                validated_rows = schema.rows_validator(rows)
                table['data'] = validated_rows
            except ReturnTable.DoesNotExist:
                result = {}
                results=[]
                for field_name in schema.fields:
                    result[field_name.name] = {
                        'value': None
                    }
                results.append(result)
                table['data']=results
        tables.append(table)
        return tables

    def log_user_action(self, action, request):
        return ReturnUserAction.log_action(self, action, request.user)

    def set_submitted(self,request):
        with transaction.atomic():
            try:
                if self.processing_status=='future' or 'due':
                    self.customer_status="under_review"
                    self.processing_status="with_curator"
                    self.submitter=request.user
                    self.save()

                #code for amendment returns is still to be added, so lodgement_date is set outside if statement
                self.lodgement_date = timezone.now()
                self.save()
                #this below code needs to be reviewed
                # self.save(version_comment='Return submitted:{}'.format(self.id))
                # self.application.save(version_comment='Return submitted:{}'.format(self.id))
                self.log_user_action(ReturnUserAction.ACTION_SUBMIT_REQUEST.format(self.id),request)
                send_external_submit_email_notification(request,self)
                # send_submit_email_notification(request,self)
            except:
                raise



class ReturnTable(RevisionedMixin):
    ret = models.ForeignKey(Return)

    name = models.CharField(max_length=50)

    class Meta:
        app_label = 'wildlifecompliance'


class ReturnRow(RevisionedMixin):
    return_table = models.ForeignKey(ReturnTable)

    data = JSONField(blank=True, null=True)

    class Meta:
        app_label = 'wildlifecompliance'


class ReturnUserAction(UserAction):
    ACTION_CREATE = "Lodge Return {}"
    ACTION_SUBMIT_REQUEST = "Submit Return {}"
    ACTION_ASSIGN_TO = "Assign to {}"
    ACTION_UNASSIGN = "Unassign"
    ACTION_DECLINE_REQUEST = "Decline request"
    ACTION_ID_REQUEST_AMENDMENTS = "Request amendments"
    ACTION_REMINDER_SENT = "Reminder sent for return {}"
    ACTION_STATUS_CHANGE = "Change status to Due for return {}"

    class Meta:
        app_label = 'wildlifecompliance'
        ordering = ('-when',)

    @classmethod
    def log_action(cls, return_obj, action, user):
        return cls.objects.create(
            return_obj=return_obj,
            who=user,
            what=str(action)
        )

    return_obj = models.ForeignKey(Return, related_name='action_logs')


class ReturnLogEntry(CommunicationsLogEntry):
    return_obj = models.ForeignKey(Return, related_name='comms_logs')

    class Meta:
        app_label = 'wildlifecompliance'

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.return_obj.id
        super(ReturnLogEntry, self).save(**kwargs)

