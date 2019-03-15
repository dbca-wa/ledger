from __future__ import unicode_literals
import os

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from ledger.accounts.models import EmailUser, Document, RevisionedMixin
from django.contrib.postgres.fields.jsonb import JSONField
#from commercialoperator.components.proposals.models import Proposal

@python_2_unicode_compatible
class Region(models.Model):
    name = models.CharField(max_length=200, unique=True)
    forest_region = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        app_label = 'commercialoperator'

    def __str__(self):
        return self.name

    # @property
    # def districts(self):
    #     return District.objects.filter(region=self)



@python_2_unicode_compatible
class District(models.Model):
    region = models.ForeignKey(Region, related_name='districts')
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=3)
    archive_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        app_label = 'commercialoperator'

    def __str__(self):
        return self.name

    @property
    def parks(self):
        return Parks.objects.filter(district=self)

    @property
    def land_parks(self):
        return Park.objects.filter(district=self, park_type='land')

    @property
    def marine_parks(self):
        return Park.objects.filter(district=self, park_type='marine')
    


@python_2_unicode_compatible
class AccessType(models.Model):
    name = models.CharField(max_length=200, blank=True)
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        app_label = 'commercialoperator'

    def __str__(self):
        return self.name

# @python_2_unicode_compatible
# class Vehicle(models.Model):
#     capacity = models.CharField(max_length=200, blank=True)
#     rego = models.CharField(max_length=200, blank=True)
#     license = models.CharField(max_length=200, blank=True)
#     access_type= models.ForeignKey(AccessType,null=True, related_name='vehicles')
#     rego_expiry= models.DateField(blank=True, null=True)

#     class Meta:
#         app_label = 'commercialoperator'

#     def __str__(self):
#         return self.rego

# @python_2_unicode_compatible
# class Park(models.Model):
#     PARK_TYPE_CHOICES = (
#         ('land', 'Land'),
#         ('marine', 'Marine'),
#         ('Film', 'Film'),
#     )
#     district = models.ForeignKey(District, related_name='parks')
#     name = models.CharField(max_length=200, unique=True)
#     code = models.CharField(max_length=10, blank=True)
#     park_type = models.CharField('Park Type', max_length=40, choices=PARK_TYPE_CHOICES,
#                                         default=PARK_TYPE_CHOICES[0][0])
#     allowed_activities = models.ManyToManyField(Activity)
#     #proposal = models.ForeignKey(Proposal, related_name='parks')
    

#     class Meta:
#         ordering = ['name']
#         app_label = 'commercialoperator'
#         #unique_together = ('id', 'proposal',)

#     def __str__(self):
#         return self.name

@python_2_unicode_compatible
class Trail(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=10, blank=True)
    

    class Meta:
        ordering = ['name']
        app_label = 'commercialoperator'
        #unique_together = ('id', 'proposal',)

    def __str__(self):
        return self.name

    @property
    def section_ids(self):
        return [i.id for i in self.sections.all()]

@python_2_unicode_compatible
class Section(models.Model):
    name = models.CharField(max_length=200, blank=True)
    visible = models.BooleanField(default=True)
    trail = models.ForeignKey(Trail, related_name='sections')

    class Meta:
        ordering = ['name']
        app_label = 'commercialoperator'

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class ActivityType(models.Model):
    ACTIVITY_TYPE_CHOICES = (
        ('land', 'Land'),
        ('marine', 'Marine'),
        ('Film', 'Film'),
    )
    type_name = models.CharField('Activity Type', max_length=40, choices=ACTIVITY_TYPE_CHOICES,
                                        default=ACTIVITY_TYPE_CHOICES[0][0])
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['type_name']
        app_label = 'commercialoperator'

    def __str__(self):
        return self.type_name

@python_2_unicode_compatible
class ActivityCategory(models.Model):
    ACTIVITY_TYPE_CHOICES = (
        ('land', 'Land'),
        ('marine', 'Marine'),
        ('Film', 'Film'),
    )
    name = models.CharField(max_length=200, blank=True)
    visible = models.BooleanField(default=True)
    activity_type = models.CharField('Activity Type', max_length=40, choices=ACTIVITY_TYPE_CHOICES,
                                        default=ACTIVITY_TYPE_CHOICES[0][0])

    class Meta:
        ordering = ['name']
        app_label = 'commercialoperator'

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Activity(models.Model):
    name = models.CharField(max_length=200, blank=True)
    visible = models.BooleanField(default=True)
    activity_category = models.ForeignKey(ActivityCategory, related_name='activities')

    class Meta:
        ordering = ['name']
        app_label = 'commercialoperator'

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class Park(models.Model):
    PARK_TYPE_CHOICES = (
        ('land', 'Land'),
        ('marine', 'Marine'),
        ('Film', 'Film'),
    )
    district = models.ForeignKey(District, related_name='parks')
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=10, blank=True)
    park_type = models.CharField('Park Type', max_length=40, choices=PARK_TYPE_CHOICES,
                                        default=PARK_TYPE_CHOICES[0][0])
    allowed_activities = models.ManyToManyField(Activity, blank=True)
    #proposal = models.ForeignKey(Proposal, related_name='parks')
    

    class Meta:
        ordering = ['name']
        app_label = 'commercialoperator'
        #unique_together = ('id', 'proposal',)

    def __str__(self):
        return self.name

    @property
    def allowed_activities_ids(self):
        return [i.id for i in self.allowed_activities.all()]

# class ParkActivity(models.Model):
#     park = models.ForeignKey(Park, blank=True, null=True, related_name='activities')
#     activity = models.ForeignKey(Activity, blank=True, null=True, related_name='parks')

#     class Meta:
#         app_label = 'commercialoperator' 
#         unique_together = ('park', 'activity')

@python_2_unicode_compatible
class ApplicationType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    visible = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']
        app_label = 'commercialoperator'

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class ActivityMatrix(models.Model):
    name = models.CharField(verbose_name='Activity matrix name', max_length=24, choices=[('Commercial Operator', u'Commercial Operator')], default='Commercial Operator')
    description = models.CharField(max_length=256, blank=True, null=True)
    schema = JSONField()
    replaced_by = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    version = models.SmallIntegerField(default=1, blank=False, null=False)
    ordered = models.BooleanField('Activities Ordered Alphabetically', default=False)

    class Meta:
        app_label = 'commercialoperator'
        unique_together = ('name', 'version')
        verbose_name_plural = "Activity matrix"

    def __str__(self):
        return '{} - v{}'.format(self.name, self.version)


@python_2_unicode_compatible
class Tenure(models.Model):
    name = models.CharField(max_length=255, unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    application_type = models.ForeignKey(ApplicationType, related_name='tenure_app_types')

    class Meta:
        ordering = ['order', 'name']
        app_label = 'commercialoperator'

    def __str__(self):
        return '{}: {}'.format(self.name, self.application_type)


@python_2_unicode_compatible
class UserAction(models.Model):
    who = models.ForeignKey(EmailUser, null=False, blank=False)
    when = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    what = models.TextField(blank=False)

    def __str__(self):
        return "{what} ({who} at {when})".format(
            what=self.what,
            who=self.who,
            when=self.when
        )

    class Meta:
        abstract = True
        app_label = 'commercialoperator'


class CommunicationsLogEntry(models.Model):
    TYPE_CHOICES = [('email', 'Email'), ('phone', 'Phone Call'), ('mail', 'Mail'), ('person', 'In Person')]
    DEFAULT_TYPE = TYPE_CHOICES[0][0]

    #to = models.CharField(max_length=200, blank=True, verbose_name="To")
    to = models.TextField(blank=True, verbose_name="To")
    fromm = models.CharField(max_length=200, blank=True, verbose_name="From")
    #cc = models.CharField(max_length=200, blank=True, verbose_name="cc")
    cc = models.TextField(blank=True, verbose_name="cc")

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DEFAULT_TYPE)
    reference = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200, blank=True, verbose_name="Subject / Description")
    text = models.TextField(blank=True)

    customer = models.ForeignKey(EmailUser, null=True, related_name='+')
    staff = models.ForeignKey(EmailUser, null=True, related_name='+')

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        app_label = 'commercialoperator'


@python_2_unicode_compatible
class Document(models.Model):
    name = models.CharField(max_length=100, blank=True,
                            verbose_name='name', help_text='')
    description = models.TextField(blank=True,
                                   verbose_name='description', help_text='')
    uploaded_date = models.DateTimeField(auto_now_add=True) 

    class Meta:
        app_label = 'commercialoperator'
        abstract = True

    @property
    def path(self):
        #return self.file.path
        return self._file.path

    @property
    def filename(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename


@python_2_unicode_compatible
class SystemMaintenance(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def duration(self):
        """ Duration of system maintenance (in mins) """
        return int( (self.end_date - self.start_date).total_seconds()/60.) if self.end_date and self.start_date else ''
        #return (datetime.now(tz=tz) - self.start_date).total_seconds()/60.
    duration.short_description = 'Duration (mins)'

    class Meta:
        app_label = 'commercialoperator'
        verbose_name_plural = "System maintenance"

    def __str__(self):
        return 'System Maintenance: {} ({}) - starting {}, ending {}'.format(self.name, self.description, self.start_date, self.end_date)
