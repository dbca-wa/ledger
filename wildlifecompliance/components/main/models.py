from __future__ import unicode_literals

from django.db import models
from django.db.models.query import QuerySet
from django.utils.encoding import python_2_unicode_compatible
from ledger.accounts.models import EmailUser
import os
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


@python_2_unicode_compatible
class Sequence(models.Model):

    name = models.CharField(
        verbose_name=_("name"),
        max_length=100,
        primary_key=True,
    )

    last = models.PositiveIntegerField(
        verbose_name=_("last value"),
    )

    class Meta:
        verbose_name = _("sequence")
        verbose_name_plural = _("sequences")

    def __str__(self):
        return "Sequence(name={}, last={})".format(
            repr(self.name), repr(self.last))


@python_2_unicode_compatible
class Region(models.Model):
    name = models.CharField(max_length=200, blank=False, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        app_label = 'wildlifecompliance'


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
        app_label = 'wildlifecompliance'


class CommunicationsLogEntry(models.Model):
    COMMUNICATIONS_LOG_TYPE_EMAIL = 'email'
    COMMUNICATIONS_LOG_TYPE_PHONE = 'phone'
    COMMUNICATIONS_LOG_TYPE_MAIL = 'mail'
    COMMUNICATIONS_LOG_TYPE_PERSON = 'person'
    TYPE_CHOICES = (
        (COMMUNICATIONS_LOG_TYPE_EMAIL, 'Email'),
        (COMMUNICATIONS_LOG_TYPE_PHONE, 'Phone Call'),
        (COMMUNICATIONS_LOG_TYPE_MAIL, 'Mail'),
        (COMMUNICATIONS_LOG_TYPE_PERSON, 'In Person')
    )

    to = models.TextField(blank=True, verbose_name="To")
    fromm = models.CharField(max_length=200, blank=True, verbose_name="From")
    cc = models.TextField(blank=True, verbose_name="cc")
    log_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=COMMUNICATIONS_LOG_TYPE_EMAIL)
    reference = models.CharField(max_length=100, blank=True)
    subject = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Subject / Description")
    text = models.TextField(blank=True)
    customer = models.ForeignKey(EmailUser, null=True, related_name='+')
    staff = models.ForeignKey(EmailUser, null=True, related_name='+')
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    class Meta:
        app_label = 'wildlifecompliance'


@python_2_unicode_compatible
class Document(models.Model):
    name = models.CharField(max_length=100, blank=True,
                            verbose_name='name', help_text='')
    description = models.TextField(blank=True,
                                   verbose_name='description', help_text='')
    uploaded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'wildlifecompliance'
        abstract = True

    @property
    def path(self):
        return self.file.path

    @property
    def filename(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.name or self.filename


# Extensions for Django's QuerySet

def computed_filter(self, **kwargs):
    kwargs['__filter'] = True
    return self.computed_filter_or_exclude(**kwargs)


def computed_exclude(self, **kwargs):
    kwargs['__filter'] = False
    return self.computed_filter_or_exclude(**kwargs)


def computed_filter_or_exclude(self, **kwargs):
    do_filter = kwargs.pop('__filter', True)
    matched_pk_list = [item.pk for item in self for (field, match) in map(
        lambda arg: (arg[0].replace('__in', ''),
                     arg[1] if isinstance(arg[1], (list, QuerySet)) else [arg[1]]
                     ), kwargs.items()
    ) if getattr(item, field) in match]
    return self.filter(pk__in=matched_pk_list) if do_filter else self.exclude(pk__in=matched_pk_list)


queryset_methods = {
    'computed_filter': computed_filter,
    'computed_exclude': computed_exclude,
    'computed_filter_or_exclude': computed_filter_or_exclude,
}


for method_name, method in queryset_methods.items():
    setattr(QuerySet, method_name, method)



class WeakLinks(models.Model):

    first_content_type = models.ForeignKey(
            ContentType, 
            related_name='first_content_type',
            on_delete=models.CASCADE)
    first_object_id = models.PositiveIntegerField()
    first_content_object = GenericForeignKey('first_content_type', 'first_object_id')

    second_content_type = models.ForeignKey(
            ContentType, 
            related_name='second_content_type',
            on_delete=models.CASCADE)
    second_object_id = models.PositiveIntegerField()
    second_content_object = GenericForeignKey('second_content_type', 'second_object_id')

    class Meta:
        app_label = 'wildlifecompliance'

    def save(self, *args, **kwargs):
        # test for existing object with first and second fields reversed.  If exists, don't create duplicate.
        duplicate = WeakLinks.objects.filter(
                first_content_type = self.second_content_type,
                second_content_type = self.first_content_type,
                first_object_id = self.second_object_id,
                second_object_id = self.first_object_id
                )
        
        if duplicate:
            print("Duplicate - no record created")
        else:
            super(WeakLinks, self).save(*args,**kwargs)

# list of approved related item models
#
# (Call_email, 'C'), (Offence, 'O'), Email_User, Inspection, ...

approved_related_item_models = [
        'Offence',
        'CallEmail',
        'Inspection',
        'SanctionOutcome',
        'Case',
        ]

def format_model_name(model_name):
    if model_name:
        lower_model_name = model_name.lower()
        switcher = {
                'callemail': 'Call / Email',
                'inspection': 'Inspection',
                'offence': 'Offence',
                'sanctionoutcome': 'Sanction Outcome',
                'case': 'Case',
                }
        return switcher.get(lower_model_name, '')

def format_url(model_name, obj_id):
    if model_name:
        lower_model_name = model_name.lower()
        switcher = {
                'callemail': '<a href=' + '/api/call_email/{}'.format(obj_id) + '>View</a>',
                'inspection': '<a href=' + '/api/inspection/{}'.format(obj_id) + '>View</a>',
                'offence': '<a href=' + '/api/offence/{}'.format(obj_id) + '>View</a>',
                'sanctionoutcome': '<a href=' + '/api/sanction_outcome/{}'.format(obj_id) + '>View</a>',
                'case': '<a href=' + '/api/case/{}'.format(obj_id) + '>View</a>',
                }
        return switcher.get(lower_model_name, '')

def get_related_items(instance, **kwargs):
    return_list = []
    # Strong links
    for f in instance._meta.get_fields():
        if f.is_relation and f.related_model.__name__ in approved_related_item_models:
            if f.is_relation and f.one_to_many:

                if instance._meta.model_name == 'callemail':
                    field_objects = f.related_model.objects.filter(call_email_id=instance.id)
                elif instance._meta.model_name == 'inspection':
                    field_objects = f.related_model.objects.filter(inspection_id=instance.id)
                elif instance._meta.model_name == 'sanctionoutcome':
                    field_objects = f.related_model.objects.filter(sanction_outcome_id=instance.id)
                elif instance._meta.model_name == 'offence':
                    field_objects = f.related_model.objects.filter(offence_id=instance.id)
                for field_object in field_objects:
                    return_list.append(
                        {   'model_name': format_model_name(f.related_model.__name__),
                            'identifier': field_object.get_related_items_identifier,
                            'descriptor': field_object.get_related_items_descriptor,
                            'action_url': format_url(f.related_model.__name__, field_object.id),
                            'link_type': 'strong',
                            'second_object_id': None,
                            'second_content_type': None,
                        })
            elif f.is_relation:
                field_value = f.value_from_object(instance)

                if field_value:
                    field_object = f.related_model.objects.get(id=field_value)

                    return_list.append(
                        {   'model_name': format_model_name(f.name),
                            'identifier': field_object.get_related_items_identifier, 
                            'descriptor': field_object.get_related_items_descriptor,
                            'action_url': format_url(f.related_model.__name__, field_object.id),
                            'link_type': 'strong',
                            'second_object_id': None,
                            'second_content_type': None,
                        })
    # Weak links - first pass with instance as first_content_object
    instance_content_type = ContentType.objects.get_for_model(type(instance))

    weak_links = WeakLinks.objects.filter(
            first_content_type__pk=instance_content_type.id,
            first_object_id=instance.id
            )
    for link in weak_links:
        link_content_type = ContentType.objects.get_for_model(
                type(
                    link.second_content_object
                    ))
        return_list.append(
            {   'model_name': format_model_name(link_content_type.model),
                'identifier': link.second_content_object.get_related_items_identifier, 
                'descriptor': link.second_content_object.get_related_items_descriptor,
                'second_object_id': link.second_content_object.id,
                'second_content_type': link_content_type.model,
                'link_type': 'weak',
                'action_url': None,
            })
    # Weak links - first pass with instance as second_content_object
    weak_links = WeakLinks.objects.filter(
            second_content_type__pk=instance_content_type.id,
            second_object_id=instance.id
            )
    for link in weak_links:
        link_content_type = ContentType.objects.get_for_model(
                type(
                    link.first_content_object
                    ))
        return_list.append(
            {   'model_name': format_model_name(link_content_type.model),
                'identifier': link.first_content_object.get_related_items_identifier, 
                'descriptor': link.first_content_object.get_related_items_descriptor,
                'second_object_id': link.first_content_object.id,
                'second_content_type': link_content_type.model,
                'link_type': 'weak',
                'action_url': None,
            })
    return return_list       

# Examples of model properties for get_related_items
@property
def get_related_items_identifier(self):
    return self.id

@property
def get_related_items_descriptor(self):
    return '{0}, {1}'.format(self.street, self.wkb_geometry)



