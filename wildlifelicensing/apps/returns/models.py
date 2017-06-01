from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields.jsonb import JSONField
from django.core.exceptions import ValidationError

import datapackage
import jsontableschema

from ledger.accounts.models import RevisionedMixin, EmailUser
from wildlifelicensing.apps.main.models import WildlifeLicenceType, WildlifeLicence, CommunicationsLogEntry


class ReturnType(models.Model):
    licence_type = models.OneToOneField(WildlifeLicenceType)
    #  data_descriptor should follow the Tabular Data Package format described at:
    #  http://data.okfn.org/doc/tabular-data-package
    #  also in:
    #  http://dataprotocols.org/data-packages/
    #  The schema inside the 'resources' must follow the JSON Table Schema defined at:
    #  http://dataprotocols.org/json-table-schema/
    data_descriptor = JSONField()

    month_frequency = models.IntegerField(choices=WildlifeLicence.MONTH_FREQUENCY_CHOICES,
                                          default=WildlifeLicence.DEFAULT_FREQUENCY)

    def clean(self):
        """
        Validate the data descriptor
        """
        #  Validate the data package
        validator = datapackage.DataPackage(self.data_descriptor)
        try:
            validator.validate()
        except Exception:
            raise ValidationError('Data package errors: {}'.format([str(e[0]) for e in validator.iter_errors()]))
        # Check that there is at least one resources defined (not required by the standard)
        if len(self.resources) == 0:
            raise ValidationError('You must define at least one resource')
        # Validate the schema for all resources
        for resource in self.resources:
            if 'schema' not in resource:
                raise ValidationError("Resource without a 'schema'.")
            else:
                schema = resource.get('schema')
                try:
                    jsontableschema.validate(schema)
                except Exception:
                    raise ValidationError(
                        'Schema errors for resource "{}": {}'.format(
                            resource.get('name'),
                            [str(e[0]) for e in jsontableschema.validator.iter_errors(schema)]))

    @property
    def resources(self):
        return self.data_descriptor.get('resources', [])

    def get_resource_by_name(self, name):
        for resource in self.resources:
            if resource.get('name') == name:
                return resource
        return None

    def get_resources_names(self):
        return [r.get('name') for r in self.resources]

    def get_schema_by_name(self, name):
        resource = self.get_resource_by_name(name)
        return resource.get('schema', {}) if resource else None


class Return(RevisionedMixin):
    STATUS_CHOICES = [
        ('current', 'Current'),
        ('future', 'Future'),
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('amendment_required', 'Amendment Required'),
        ('amended', 'Amended'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    ]
    DEFAULT_STATUS = STATUS_CHOICES[1][0]

    CUSTOMER_EDITABLE_STATE = ['current', 'draft', 'amendment_required']

    return_type = models.ForeignKey(ReturnType)
    licence = models.ForeignKey(WildlifeLicence)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DEFAULT_STATUS)

    lodgement_number = models.CharField(max_length=9, blank=True, default='')

    lodgement_date = models.DateField(blank=True, null=True)

    due_date = models.DateField(null=False, blank=False)

    proxy_customer = models.ForeignKey(EmailUser, blank=True, null=True)

    nil_return = models.BooleanField(default=False)

    comments = models.TextField(blank=True, null=True)

    @property
    def reference(self):
        return '{}'.format(self.lodgement_number)

    @property
    def can_user_edit(self):
        """
        :return: True if the return is in one of the editable status.
        """
        return self.status in self.CUSTOMER_EDITABLE_STATE

    @property
    def pending_amendments_qs(self):
        return ReturnAmendmentRequest.objects.filter(ret=self, status='requested')


class ReturnAmendmentRequest(models.Model):
    STATUS_CHOICES = (('requested', 'Requested'), ('amended', 'Amended'))

    ret = models.ForeignKey(Return)
    status = models.CharField('Status', max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    reason = models.TextField(blank=False)
    officer = models.ForeignKey(EmailUser, null=True)


class ReturnTable(RevisionedMixin):
    ret = models.ForeignKey(Return)

    name = models.CharField(max_length=50)


class ReturnRow(RevisionedMixin):
    return_table = models.ForeignKey(ReturnTable)

    data = JSONField(blank=True, null=True)


class ReturnLogEntry(CommunicationsLogEntry):
    ret = models.ForeignKey(Return)

    def save(self, **kwargs):
        # save the application reference if the reference not provided
        if not self.reference:
            self.reference = self.ret.reference
        super(ReturnLogEntry, self).save(**kwargs)
