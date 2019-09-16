import traceback
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from django.core.exceptions import ValidationError
from wildlifecompliance.components.offence.models import Offender
from wildlifecompliance.components.organisations.models import Organisation
from ledger.accounts.models import EmailUser
from django.db import models
from rest_framework import serializers
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import logging

logger = logging.getLogger(__name__)


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
    comment = models.CharField(max_length=255, blank=True)

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
        related_items = get_related_items(self.first_content_object)
        second_object_identifier = self.second_content_object.get_related_items_identifier
        second_object_formatted_model_name = format_model_name(self.second_content_object._meta.model_name)
        duplicate_related_item_exists = False
        if related_items:
            for item in related_items:
                if (self.second_content_object.get_related_items_identifier == item.get('identifier') and 
                        format_model_name(self.second_content_object._meta.model_name) == item.get('model_name')):
                    duplicate_related_item_exists = True
                    log_message =  'Duplicate RelatedItem/WeakLink - no record created for {} with pk {}'.format(
                                self.first_content_type.model,
                                self.first_object_id)
                    logger.debug(log_message)
        if duplicate_related_item_exists:
            log_message =  'Duplicate RelatedItem/WeakLink - no record created for {} with pk {}'.format(
                        self.first_content_type.model,
                        self.first_object_id)
            logger.debug(log_message)
        elif self.second_content_type and self.second_content_type.model not in [i.lower() for i in approved_related_item_models]:
            log_message =  'Incorrect model type - no record created for {} with pk {}'.format(
                        self.first_content_type.model,
                        self.first_object_id)
            logger.debug(log_message)
        elif duplicate:
            log_message =  'Duplicate WeakLink - no record created for {} with pk {}'.format(
                        self.first_content_type.model,
                        self.first_object_id)
            logger.debug(log_message)
        else:
            super(WeakLinks, self).save(*args,**kwargs)


class RelatedItemsSerializer(serializers.Serializer):
    descriptor = serializers.CharField()
    identifier = serializers.CharField()
    model_name = serializers.CharField()
    second_object_id = serializers.IntegerField(allow_null=True)
    second_content_type = serializers.CharField(allow_blank=True)
    weak_link = serializers.BooleanField()
    action_url = serializers.CharField(allow_blank=True)
    comment = serializers.CharField()


class RelatedItem:

    def __init__(self, model_name, identifier, descriptor, 
            action_url, weak_link=False, second_object_id=None, second_content_type=None, comment=None):
        self.model_name = model_name
        self.identifier = identifier
        self.descriptor = descriptor
        self.action_url = action_url
        self.weak_link = weak_link
        self.second_object_id = second_object_id
        self.second_content_type = second_content_type
        self.comment = comment


def search_weak_links(request_data):
    from wildlifecompliance.components.call_email.models import CallEmail
    from wildlifecompliance.components.inspection.models import Inspection
    from wildlifecompliance.components.offence.models import Offence
    from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome
    qs = []

    components_selected = request_data.get('selectedEntity')
    search_text = request_data.get('searchText')
    if 'call_email' in components_selected:
        qs = CallEmail.objects.filter(
                Q(number__icontains=search_text) |
                Q(caller__icontains=search_text) |
                Q(caller_phone_number__icontains=search_text) |
                Q(location__street__icontains=search_text) |
                Q(location__town_suburb__icontains=search_text) 
                )
    elif 'inspection' in components_selected:
        qs = Inspection.objects.filter(
                Q(number__icontains=search_text) |
                Q(title__icontains=search_text) |
                Q(details__icontains=search_text) |
                Q(inspection_type__inspection_type__icontains=search_text) |
                Q(individual_inspected__first_name__icontains=search_text) |
                Q(individual_inspected__last_name__icontains=search_text) |
                Q(call_email__number__icontains=search_text)
                )
    elif 'offence' in components_selected:
        qs = Offence.objects.filter(
                Q(lodgement_number__icontains=search_text) |
                Q(identifier__icontains=search_text) |
                Q(details__icontains=search_text) |
                Q(alleged_offences__act__icontains=search_text) |
                Q(alleged_offences__name__icontains=search_text) |
                Q(offender__person__first_name__icontains=search_text) |
                Q(offender__person__last_name__icontains=search_text)
                )
    elif 'sanction_outcome' in components_selected:
        qs = SanctionOutcome.objects.filter(
                Q(lodgement_number__icontains=search_text) |
                Q(identifier__icontains=search_text) |
                Q(description__icontains=search_text) |
                Q(offence__alleged_offences__act__icontains=search_text) |
                Q(offence__alleged_offences__name__icontains=search_text) |
                Q(offender__person__first_name__icontains=search_text) |
                Q(offender__person__last_name__icontains=search_text)
                )
    return_qs = []

    # First 10 records only
    for item in qs[:10]:

        return_qs.append({
            'id': item.id,
            'model_name': item._meta.model_name,
            'item_identifier': item.get_related_items_identifier,
            'item_description': item.get_related_items_descriptor,
            })
    return return_qs

# list of approved related item models
approved_related_item_models = [
        'Offence',
        'CallEmail',
        'Inspection',
        'SanctionOutcome',
        'Case',
        'EmailUser',
        'Organisation',
        'Offender',
        ]

approved_email_user_related_items = [
        'volunteer',
        'individual_inspected',
        'email_user',
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
                'emailuser': 'Person',
                'organisation': 'Organisation',
                }
        return switcher.get(lower_model_name, '')

def format_url(model_name, obj_id):
    if model_name:
        lower_model_name = model_name.lower()
        obj_id_str = str(obj_id)
        switcher = {
                'callemail': '<a href=/internal/call_email/' + obj_id_str + ' target="_blank">View</a>',
                'inspection': '<a href=/internal/inspection/' + obj_id_str + ' target="_blank">View</a>',
                'offence': '<a href=/internal/offence/' + obj_id_str + ' target="_blank">View</a>',
                'sanctionoutcome': '<a href=/internal/sanction_outcome/' + obj_id_str + ' target="_blank">View</a>',
                'case': '<a href=/internal/case/' + obj_id_str + ' target="_blank">View</a>',
                'emailuser': '<a href=/internal/users/' + obj_id_str + ' target="_blank">View</a>',
                'organisation': '<a href=/internal/organisations/' + obj_id_str + ' target="_blank">View</a>',
                }
        return switcher.get(lower_model_name, '')

def get_related_offenders(entity, **kwargs):
    offender_list = []
    offenders = []
    if entity._meta.model_name == 'sanctionoutcome':
        offenders.append(entity.offender)
    if entity._meta.model_name == 'offence':
        offenders = Offender.objects.filter(offence_id=entity.id)
    for offender in offenders:
        if offender.person and not offender.removed:
            user = EmailUser.objects.get(id=offender.person.id)
            offender_list.append(user)
        if offender.organisation and not offender.removed:
            organisation = Organisation.objects.get(id=offender.organisation.id)
            offender_list.append(organisation)
    return offender_list

def get_related_items(entity, **kwargs):
    try:
        return_list = []
        # Strong links
        for f in entity._meta.get_fields():
            if f.is_relation and f.related_model.__name__ in approved_related_item_models:
                # foreign keys from other objects to entity
                if f.is_relation and f.one_to_many:
                    if entity._meta.model_name == 'callemail':
                        field_objects = f.related_model.objects.filter(call_email_id=entity.id)
                    elif entity._meta.model_name == 'inspection':
                        field_objects = f.related_model.objects.filter(inspection_id=entity.id)
                    elif entity._meta.model_name == 'sanctionoutcome':
                        field_objects = f.related_model.objects.filter(sanction_outcome_id=entity.id)
                    elif entity._meta.model_name == 'offence' and f.name == 'offender':
                        field_objects = get_related_offenders(entity)
                    elif entity._meta.model_name == 'offence':
                        field_objects = f.related_model.objects.filter(offence_id=entity.id)
                    for field_object in field_objects:
                        related_item = RelatedItem(
                                model_name = format_model_name(f.related_model.__name__),
                                identifier = field_object.get_related_items_identifier,
                                descriptor = field_object.get_related_items_descriptor,
                                action_url = format_url(
                                        model_name=f.related_model.__name__,
                                        obj_id=field_object.id
                                        )
                                )
                        return_list.append(related_item)
                # foreign keys from entity to EmailUser
                elif f.is_relation and f.related_model._meta.model_name == 'emailuser':
                    field_value = f.value_from_object(entity)
                    if field_value and f.name in approved_email_user_related_items:
                        field_object = f.related_model.objects.get(id=field_value)
                        related_item = RelatedItem(
                                model_name = format_model_name(f.related_model.__name__),
                                identifier = field_object.get_related_items_identifier,
                                descriptor = field_object.get_related_items_descriptor,
                                action_url = format_url(
                                        model_name=f.related_model.__name__,
                                        obj_id=field_object.id
                                        )
                                )
                        return_list.append(related_item)
                # remaining entity foreign keys
                elif f.is_relation:
                    field_object = None
                    # Sanction Outcome FK to Offender
                    if f.name == 'offender':
                        field_object_list = get_related_offenders(entity)
                        # There will only ever be one at most
                        if field_object_list:
                            field_object = field_object_list[0]
                    # All other FKs
                    else:
                        field_value = f.value_from_object(entity)
                        if field_value:
                            field_object = f.related_model.objects.get(id=field_value)
                    if field_object:
                        related_item = RelatedItem(
                                model_name = format_model_name(field_object._meta.model_name),
                                identifier = field_object.get_related_items_identifier,
                                descriptor = field_object.get_related_items_descriptor,
                                action_url = format_url(
                                        model_name=field_object._meta.model_name,
                                        obj_id=field_object.id
                                        )
                                )
                        return_list.append(related_item)

        # Weak links - first pass with instance as first_content_object
        entity_content_type = ContentType.objects.get_for_model(type(entity))

        weak_links = WeakLinks.objects.filter(
                first_content_type__pk=entity_content_type.id,
                first_object_id=entity.id
                )
        for link in weak_links:
            link_content_type = ContentType.objects.get_for_model(
                    type(
                        link.second_content_object
                        ))
            if link_content_type.model in [i.lower() for i in approved_related_item_models]:
                related_item = RelatedItem(
                        model_name =  format_model_name(link_content_type.model),
                        identifier = link.second_content_object.get_related_items_identifier,
                        descriptor = link.second_content_object.get_related_items_descriptor,
                        second_object_id = link.second_content_object.id,
                        second_content_type = link_content_type.model,
                        weak_link = True,
                        action_url = format_url(
                                model_name=link_content_type.model,
                                obj_id=link.second_content_object.id
                                ),
                        comment = link.comment
                        )
                return_list.append(related_item)

        # Weak links - first pass with instance as second_content_object
        weak_links = WeakLinks.objects.filter(
                second_content_type__pk=entity_content_type.id,
                second_object_id=entity.id
                )
        for link in weak_links:
            link_content_type = ContentType.objects.get_for_model(
                    type(
                        link.first_content_object
                        ))
            if link_content_type.model in [i.lower() for i in approved_related_item_models]:
                related_item = RelatedItem(
                        model_name = format_model_name(link_content_type.model),
                        identifier = link.first_content_object.get_related_items_identifier,
                        descriptor = link.first_content_object.get_related_items_descriptor,
                        second_object_id = link.first_content_object.id,
                        second_content_type = link_content_type.model,
                        weak_link = True,
                        action_url = format_url(
                                model_name=link_content_type.model,
                                obj_id=link.first_content_object.id
                                ),
                        comment = link.comment
                        )
                return_list.append(related_item)
        
        serializer = RelatedItemsSerializer(return_list, many=True)
        return serializer.data
    except serializers.ValidationError:
        print(traceback.print_exc())
        raise
    except ValidationError as e:
        print(traceback.print_exc())
        raise serializers.ValidationError(repr(e.error_dict))
    except Exception as e:
        print(traceback.print_exc())
        raise serializers.ValidationError(str(e))


# Examples of model properties for get_related_items
@property
def get_related_items_identifier(self):
    return self.id

@property
def get_related_items_descriptor(self):
    return '{0}, {1}'.format(self.street, self.wkb_geometry)
# End examples

