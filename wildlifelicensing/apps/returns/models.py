from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields.jsonb import JSONField

from ledger.accounts.models import RevisionedMixin
from wildlifelicensing.apps.main.models import WildlifeLicenceType, WildlifeLicence


class ReturnType(models.Model):
    licence_type = models.OneToOneField(WildlifeLicenceType)
    data_descriptor = JSONField()

    month_frequency = models.IntegerField(choices=WildlifeLicence.MONTH_FREQUENCY_CHOICES,
                                          default=WildlifeLicence.DEFAULT_FREQUENCY)

    def get_schema_names(self):
        resources = self.data_descriptor.get('resources', [])

        names = []
        for resource in resources:
            if 'name' in resource:
                names.append(resource.get('name'))

        return names

    def get_schema(self, table_name):
        resources = self.data_descriptor.get('resources', [])

        for resource in resources:
            if resource.get('name') == table_name:
                return resource.get('schema', {})

        return None


class Return(RevisionedMixin):
    STATUS_CHOICES = [('new', 'New'), ('draft', 'Draft'), ('submitted', 'Submitted'),
                      ('accepted', 'Accepted'), ('declined', 'Declined')]

    DEFAULT_STATUS = STATUS_CHOICES[0][0]

    return_type = models.ForeignKey(ReturnType)
    licence = models.ForeignKey(WildlifeLicence)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DEFAULT_STATUS)

    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    lodgement_sequence = models.IntegerField(blank=True, default=0)
    lodgement_date = models.DateField(blank=True, null=True)

    due_date = models.DateField(null=False, blank=False)


class ReturnTable(RevisionedMixin):
    ret = models.ForeignKey(Return)

    name = models.CharField(max_length=50)


class ReturnRow(RevisionedMixin):
    return_table = models.ForeignKey(ReturnTable)

    data = JSONField(blank=True, null=True)
