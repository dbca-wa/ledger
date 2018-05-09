from __future__ import unicode_literals

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from ledger.accounts.models import EmailUser, Document, RevisionedMixin

@python_2_unicode_compatible
class Region(models.Model):
    name = models.CharField(max_length=200, unique=True)
    forest_region = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']
        app_label = 'disturbance'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class District(models.Model):
    region = models.ForeignKey(Region, related_name='districts')
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=3)
    archive_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        app_label = 'disturbance'

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class ApplicationType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        app_label = 'disturbance'

    def __str__(self):
        return self.name
 
@python_2_unicode_compatible
class Activity(models.Model):
    name = models.CharField(max_length=255, unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    application_type = models.ForeignKey(ApplicationType, related_name='activity_app_types')

    class Meta:
        ordering = ['order', 'name']
        app_label = 'disturbance'

    def __str__(self):
        return '{}: {}'.format(self.name, self.application_type)

@python_2_unicode_compatible
class Tenure(models.Model):
    name = models.CharField(max_length=255, unique=True)
    order = models.PositiveSmallIntegerField(default=0)
    application_type = models.ForeignKey(ApplicationType, related_name='tenure_app_types')

    class Meta:
        ordering = ['order', 'name']
        app_label = 'disturbance'

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
        app_label = 'disturbance'

class CommunicationsLogEntry(models.Model):
    TYPE_CHOICES = [('email', 'Email'), ('phone', 'Phone Call'), ('mail', 'Mail'), ('person', 'In Person')]
    DEFAULT_TYPE = TYPE_CHOICES[0][0]

    to = models.CharField(max_length=200, blank=True, verbose_name="To")
    fromm = models.CharField(max_length=200, blank=True, verbose_name="From")
    cc = models.CharField(max_length=200, blank=True, verbose_name="cc")

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DEFAULT_TYPE)
    reference = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200, blank=True, verbose_name="Subject / Description")
    text = models.TextField(blank=True)

    customer = models.ForeignKey(EmailUser, null=True, related_name='+')
    staff = models.ForeignKey(EmailUser, null=True, related_name='+')

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        app_label = 'disturbance'

@python_2_unicode_compatible
class Document(models.Model):
    name = models.CharField(max_length=100, blank=True,
                            verbose_name='name', help_text='')
    description = models.TextField(blank=True,
                                   verbose_name='description', help_text='')
    uploaded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'disturbance'
        abstract = True

    @property
    def path(self):
        return self.file.path

    @property
    def filename(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename
