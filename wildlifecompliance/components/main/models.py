from __future__ import unicode_literals

from django.db import models
from django.db.models.query import QuerySet
from django.utils.encoding import python_2_unicode_compatible
from ledger.accounts.models import EmailUser
import os


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

# list of approved related item models
#
# (Call_email, 'C'), (Offence, 'O'), Email_User, Inspection, ...

approved_related_item_models = [
        'Offence',
        ]

def get_related_items(self, **kwargs):
    # import ipdb; ipdb.set_trace()
    return_list = []
    for f in self._meta.get_fields():
        if f.is_relation and f.related_model.__name__ in approved_related_item_models:
            # Get foreign key related fields
            # TODO add approved related models list and compare to f.name
            # if f.is_relation and (f.one_to_many or f.many_to_one): # include related item models
            if f.is_relation and f.one_to_many: # include related item models
                print(f)
                #field_value = f.field.value_from_object(f.field.model)
                # print(field_value)

                field_objects = f.related_model.objects.filter(call_email_id=self.id)
                for field_object in field_objects:
                    print(field_object)
                    return_list.append(
                        {   'model_name': f.name,
                            'get_related_items_identifier': field_object.get_related_items_identifier, 
                            'get_related_items_descriptor': field_object.get_related_items_descriptor
                        })
            elif f.is_relation:
                print(f)
                field_value = f.value_from_object(self)

                if field_value:
                    field_object = f.related_model.objects.get(id=field_value)

                    return_list.append(
                        {   'model_name': f.name,
                            'get_related_items_identifier': field_object.get_related_items_identifier, 
                            'get_related_items_descriptor': field_object.get_related_items_descriptor
                        })
    return return_list       

# Examples of model properties for get_related_items
@property
def get_related_items_identifier(self):
    return self.id

@property
def get_related_items_descriptor(self):
    return '{0}, {1}'.format(self.street, self.wkb_geometry)
