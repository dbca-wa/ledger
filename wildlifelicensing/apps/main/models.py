from __future__ import unicode_literals, print_function, absolute_import, division

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.postgres.fields.jsonb import JSONField
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.conf import settings

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

    class Meta:
        verbose_name_plural = 'Wildlife licence categories'


class WildlifeLicenceType(LicenceType):
    product_title = models.CharField(max_length=64, unique=True)
    identification_required = models.BooleanField(default=False)
    senior_applicable = models.BooleanField(default=False)
    default_period = models.PositiveIntegerField('Default Licence Period (days)', blank=True, null=True)
    default_conditions = models.ManyToManyField(Condition, through='DefaultCondition', blank=True)
    application_schema = JSONField(blank=True, null=True)
    category = models.ForeignKey(WildlifeLicenceCategory, null=True, blank=True)
    variant_group = models.ForeignKey('VariantGroup', null=True, blank=True)
    help_text = models.TextField(blank=True)

    def clean(self):
        """
        Pre save validation:
        - A payment product and all its variants must exist before creating a LicenceType.
        - Check for senior voucher if applicable.
        :return: raise an exception if error
        """
        variant_codes = payment_utils.generate_product_title_variants(self)

        missing_product_variants = []

        for variant_code in variant_codes:
            if payment_utils.get_product(variant_code) is None:
                missing_product_variants.append(variant_code)

        if missing_product_variants:
            msg = mark_safe("The payments products with titles matching the below list of product codes were not "
                            "found. Note: You must create a payment product(s) for a new licence type and all its "
                            "variants, even if the licence has no fee. <ul><li>{}</li></ul>".
                            format('</li><li>'.join(missing_product_variants)))

            raise ValidationError(msg)

        if self.senior_applicable and payment_utils.get_voucher(settings.WL_SENIOR_VOUCHER_CODE) is None:
            msg = mark_safe("The senior voucher with code={} cannot be found. It must be created before setting a "
                            "licence type to be senior applicable.<br>"
                            "Note: the senior voucher code can be changed in the settings of the application."
                            .format(settings.WL_SENIOR_VOUCHER_CODE))
            raise ValidationError(msg)


@python_2_unicode_compatible
class WildlifeLicence(Licence):
    MONTH_FREQUENCY_CHOICES = [(-1, 'One off'), (1, 'Monthly'), (3, 'Quarterly'), (6, 'Twice-Yearly'), (12, 'Yearly')]
    DEFAULT_FREQUENCY = MONTH_FREQUENCY_CHOICES[0][0]

    profile = models.ForeignKey(Profile)
    purpose = models.TextField(blank=True)
    locations = models.TextField(blank=True)
    cover_letter_message = models.TextField(blank=True)
    additional_information = models.TextField(blank=True)
    licence_document = models.ForeignKey(Document, blank=True, null=True, related_name='licence_document')
    cover_letter_document = models.ForeignKey(Document, blank=True, null=True, related_name='cover_letter_document')
    return_frequency = models.IntegerField(choices=MONTH_FREQUENCY_CHOICES, default=DEFAULT_FREQUENCY)
    replaced_by = models.ForeignKey('self', blank=True, null=True)
    regions = models.ManyToManyField(Region, blank=False)
    variants = models.ManyToManyField('Variant', blank=True, through='WildlifeLicenceVariantLink')
    renewal_sent = models.BooleanField(default=False)
    extracted_fields = JSONField(blank=True, null=True)

    def __str__(self):
        return self.reference

    def get_title_with_variants(self):
        if self.pk is not None and self.variants.exists():
            return '{} ({})'.format(self.licence_type.name,
                                    ' / '.join(self.variants.all().values_list('name', flat=True)))
        else:
            return self.licence_type.name

    @property
    def reference(self):
        return '{}-{}'.format(self.licence_number, self.licence_sequence)

    @property
    def is_issued(self):
        return self.licence_number is not None and len(self.licence_number) > 0

    def search_extracted_fields(self,search):
        extracted_fields = self.extracted_fields

        if search == '': return ''

        authorised_persons = []
        all_species = []
        # information extracted from application
        if extracted_fields:
            for field in extracted_fields:
                if 'children' in field and field['type'] == 'group':
                    if search in field['name']:
                        if search == 'authorised_persons':
                            authorised_person = {
                                'given_names': '',
                                'surname': ''
                            }
                            for index, group in enumerate(field['children']):
                                for child_field in group:
                                    # Get surname
                                    if 'surname' in child_field['name'] and 'data' in child_field and child_field['data']:
                                        authorised_person['surname'] = child_field['data']
                                    elif 'given_names' in child_field['name'] and 'data' in child_field and child_field['data']:
                                        authorised_person['given_names'] = child_field['data']
                                name = '{} {}'.format(authorised_person['surname'],authorised_person['given_names'])
                                authorised_persons.append(name)
                        elif search == 'species_estimated_number':
                            species = {
                                'name':'',
                                'number':''
                            }
                            for index, group in enumerate(field['children']):
                                for child_field in group:
                                    # Get surname
                                    if 'species_causing_damage' in child_field['name'] and 'data' in child_field and child_field['data']:
                                        species['name'] = child_field['data']
                                    elif 'number_causing_damage' in child_field['name'] and 'data' in child_field and child_field['data']:
                                        species['number'] = child_field['data']
                                name = '{} : {}'.format(species['name'],species['number'])
                                all_species.append(name)

        if search == 'authorised_persons':
            return authorised_persons
        elif search == 'species_estimated_number':
            return all_species
        else:
            return ''


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
    cc = models.CharField(max_length=200, blank=True, verbose_name="cc")

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DEFAULT_TYPE)
    reference = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=200, blank=True, verbose_name="Subject / Description")
    text = models.TextField(blank=True)
    documents = models.ManyToManyField(Document, blank=True)

    customer = models.ForeignKey(EmailUser, null=True, related_name='customer')
    staff = models.ForeignKey(EmailUser, null=True, related_name='staff')

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)


@python_2_unicode_compatible
class Variant(models.Model):
    name = models.CharField(max_length=200)
    product_title = models.CharField(max_length=64, unique=True)
    help_text = models.TextField(blank=True)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class VariantGroup(models.Model):
    name = models.CharField(max_length=50)
    child = models.ForeignKey('self', null=True, blank=True)
    variants = models.ManyToManyField(Variant)

    def clean(self):
        """
        Guards against putting itself as child
        :return:
        """
        if self.child and self.child.pk == self.pk:
            raise ValidationError("Can't put yourself as a child")

    def __str__(self):
        if self.child is None or self.child.pk == self.pk:
            return self.name
        else:
            return '{} > {}'.format(self.name, self.child.__str__())


class WildlifeLicenceVariantLink(models.Model):
    licence = models.ForeignKey(WildlifeLicence)
    variant = models.ForeignKey(Variant)
    order = models.IntegerField()


@python_2_unicode_compatible
class AssessorGroup(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    members = models.ManyToManyField(EmailUser, blank=True)
    purpose = models.BooleanField(default=False)

    def __str__(self):
        return self.name


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
