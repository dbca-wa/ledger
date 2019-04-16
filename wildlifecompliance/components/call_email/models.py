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
    NAME_CHOICES = (
            ('complaint', 'Complaint'),
            ('enquiry', 'Enquiry'),
            ('incident', 'Incident'),
            )

    name = models.CharField(
            max_length=30,
            choices=NAME_CHOICES,
            default=NAME_CHOICES[0][0]            
            )

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Classification'
        verbose_name_plural = 'CM_Classifications'

    def __str__(self):
        return self.get_name_display()


class Location(models.Model):

    STATE_CHOICES = (
            ('WA', 'Western Australia'),
            ('VIC', 'Victoria'),
            ('QLD', 'Queensland'),
            ('NSW', 'New South Wales'),
            ('TAS', 'Tasmania'),
            ('NT', 'Northern Territory'),
            ('ACT', 'Australian Capital Territory')
            )

    latitude = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    street = models.CharField(max_length=100)
    town_suburb = models.CharField(max_length=100)
    state = models.CharField(max_length=50, choices=STATE_CHOICES, default='WA')
    postcode = models.IntegerField()
    country = models.CharField(max_length=100, default='Australia')

    class Meta:
        app_label='wildlifecompliance'
        verbose_name = 'CM_Location'
        verbose_name_plural = 'CM_Locations'

    def __str__(self):
        return '{0}, {1}, {2}, {3}, {4}' \
                .format(self.latitude, self.longitude, self.street, self.town_suburb, self.state)


class ReportType(models.Model):

    report_type = models.CharField(max_length=50)
    schema = JSONField(null=True)
    version = models.SmallIntegerField(default=1, blank=False, null=False)
    description = models.CharField(max_length=256, blank=True, null=True)
    replaced_by = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        app_label='wildlifecompliance'
        verbose_name = 'CM_ReportType'
        verbose_name_plural = 'CM_ReportTypes'
        unique_together = ('report_type', 'version')

    def __str__(self):
        return self.report_type


class Referrer(models.Model):
    name = models.CharField(max_length=50, blank=True)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Referrer'
        verbose_name_plural = 'CM_Referrers'

    def __str__(self):
        return self.name


class CallEmail(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('open_followup', 'Open (follow-up)'),
        ('open_inspection', 'Open (Inspection)'),
        ('open_case', 'Open (Case)'),
        ('closed', 'Closed'),
    )

    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        default=STATUS_CHOICES[0][0])
    location = models.ForeignKey(
            Location,
            null=True,
            )
    classification = models.ForeignKey(
            Classification, 
            )
    data = JSONField(default=list)
    schema = JSONField(default=list)
    lodged_on = models.DateField(auto_now_add=True)
    number = models.CharField(max_length=50)
    caller = models.CharField(max_length=100)
    assigned_to = models.CharField(max_length=100)
    anonymous_call = models.BooleanField(default=False)
    caller_wishes_to_remain_anonymous = models.BooleanField(default=False)
    occurrence_date_from = models.DateField(null=True)
    occurrence_time_from = models.TimeField(null=True)
    occurrence_date_to = models.DateField(null=True)
    occurrence_time_to = models.TimeField(null=True)
    report_type = models.ForeignKey(
            ReportType,
            null=True
            )

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Call/Email'
        verbose_name_plural = 'CM_Calls/Emails'

    def __str__(self):
        return 'ID: {0}, Status: {1}, Number: {2}, Caller: {3}, Assigned To: {4}' \
                .format(self.id, self.status, self.number, self.caller, self.assigned_to)

