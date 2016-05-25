from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields.jsonb import JSONField

from ledger.accounts.models import RevisionedMixin
from wildlifelicensing.apps.main.models import WildlifeLicenceType, WildlifeLicence


class ReturnType(models.Model):
    licence_type = models.OneToOneField(WildlifeLicenceType)
    additional_data_descriptors = JSONField(blank=True, null=True)


class Return(RevisionedMixin):
    STATUS_CHOICES = (('draft', 'Draft'), ('submitted', 'Submitted'),
                      ('accepted', 'Accepted'), ('declined', 'Declined'))

    models.ForeignKey(ReturnType)
    models.ForeignKey(WildlifeLicence)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    lodgement_sequence = models.IntegerField(blank=True, default=0)
    lodgement_date = models.DateField(blank=True, null=True)


class ReturnRow(RevisionedMixin):
    models.ForeignKey(Return)

    species = models.CharField(max_length=200)
    species_count = models.IntegerField()
    latitude = models.DecimalField(decimal_places=3, max_digits=6)
    longitude = models.DecimalField(decimal_places=3, max_digits=6)

    additional_data = JSONField(blank=True, null=True)
