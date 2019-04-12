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
        #return '{}'.format(self.name)
        # return self.get_name_display()
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
       return str(self.street)


class ReportType(models.Model):
    TYPE_CHOICES = (
            ('bird', 'Bird'),
            ('mammal', 'Mammal'),
            ('snake', 'Snake'),
            ('reptile', 'Reptile'),
            ('amphibian', 'Amphibian'),
            ('non-wildlife', 'Non-Wildlife'),
            ('other', 'Other'),
            )

    report_type = models.CharField(
            max_length=50, 
            choices=TYPE_CHOICES,
            default='bird'
            )

    schema = JSONField(default=list)

    class Meta:
        app_label='wildlifecompliance'
        verbose_name = 'CM_ReportType'
        verbose_name_plural = 'CM_ReportTypes'

    def __str__(self):
        return self.get_report_type_display()


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

    #classification = models.CharField(max_length=30) # this should be a FK to Admin enum list
    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        default=STATUS_CHOICES[0][0])
    location = models.ForeignKey(
            Location,
            null=True,
            #default=1,
            )
    classification = models.ForeignKey(
            Classification, 
            # default=1,
            # related_name='calls'
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
        return str(self.id)

