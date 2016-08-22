from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.postgres.fields.jsonb import JSONField
from django.core.exceptions import ValidationError

from ledger.accounts.models import RevisionedMixin, EmailUser, Document, Profile
from ledger.licence.models import LicenceType, Licence

from wildlifelicensing.apps.payments import utils as payment_utils


@python_2_unicode_compatible
class Condition(RevisionedMixin):
    text = models.TextField()
    code = models.CharField(max_length=10, unique=True)
    one_off = models.BooleanField(default=False)
    obsolete = models.BooleanField(default=False)

    def __str__(self):
        return self.code


@python_2_unicode_compatible
class Region(models.Model):
    name = models.CharField(max_length=200, blank=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


@python_2_unicode_compatible
class WildlifeLicenceCategory(models.Model):
    name = models.CharField(max_length=100, blank=False, unique=True)

    def __str__(self):
        return self.name


class WildlifeLicenceType(LicenceType):
    code_slug = models.SlugField(max_length=64, unique=True)
    identification_required = models.BooleanField(default=False)
    default_conditions = models.ManyToManyField(Condition, through='DefaultCondition', blank=True)
    application_schema = JSONField(blank=True, null=True)
    category = models.ForeignKey(WildlifeLicenceCategory, null=True, blank=True)

    def clean(self):
        """
        Pre save validation:
        - A payment product must exist before creating a LicenceType. Even if the licence is free, a product with price=0
        must be created.
        :return: raise an exception if error
        """
        if payment_utils.get_product(self) is None:
            msg = "Payment product not found." \
                  "You must create a payment product before creating a new Licence Type, even if the licence is free."
            raise ValidationError(msg)


@python_2_unicode_compatible
class WildlifeLicence(Licence):
    MONTH_FREQUENCY_CHOICES = [(-1, 'One off'), (1, 'Monthly'), (3, 'Quarterly'), (6, 'Twice-Yearly'), (12, 'Yearly')]
    DEFAULT_FREQUENCY = MONTH_FREQUENCY_CHOICES[0][0]

    profile = models.ForeignKey(Profile)
    sequence_number = models.IntegerField(default=1)
    purpose = models.TextField(blank=True)
    locations = models.TextField(blank=True)
    cover_letter_message = models.TextField(blank=True)
    additional_information = models.TextField(blank=True)
    licence_document = models.ForeignKey(Document, blank=True, null=True, related_name='licence_document')
    cover_letter_document = models.ForeignKey(Document, blank=True, null=True, related_name='cover_letter_document')
    return_frequency = models.IntegerField(choices=MONTH_FREQUENCY_CHOICES, default=DEFAULT_FREQUENCY)
    previous_licence = models.ForeignKey('self', blank=True, null=True)
    regions = models.ManyToManyField(Region, blank=True)

    def __str__(self):
        return self.reference

    @property
    def reference(self):
        return '{}-{}'.format(self.licence_number, self.sequence_number)


class DefaultCondition(models.Model):
    condition = models.ForeignKey(Condition)
    wildlife_licence_type = models.ForeignKey(WildlifeLicenceType)
    order = models.IntegerField()

    class Meta:
        unique_together = ('condition', 'wildlife_licence_type', 'order')


class CommunicationsLogEntry(models.Model):
    TYPE_CHOICES = [('email', 'Email'), ('phone', 'Phone Call'), ('main', 'Mail'), ('person', 'In Person')]
    DEFAULT_TYPE = TYPE_CHOICES[0][0]

    to = models.CharField(max_length=200, blank=True, verbose_name="To")
    fromm = models.CharField(max_length=200, blank=True, verbose_name="From")

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DEFAULT_TYPE)
    subject = models.CharField(max_length=200, blank=True, verbose_name="Subject / Description")
    text = models.TextField(blank=True)
    document = models.ForeignKey(Document, null=True, blank=False)

    customer = models.ForeignKey(EmailUser, null=True, related_name='customer')
    officer = models.ForeignKey(EmailUser, null=True, related_name='officer')

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)


@python_2_unicode_compatible
class AssessorGroup(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    members = models.ManyToManyField(EmailUser, blank=True)
    purpose = models.BooleanField(default=False)

    def __str__(self):
        return self.name
