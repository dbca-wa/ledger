import traceback
from django.contrib.contenttypes.models import ContentType
from wildlifecompliance.components.main.models import WeakLinks
from serializers import RelatedItemsSerializer
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from django.core.exceptions import ValidationError
from utils import approved_related_item_models


class RelatedItem:

    def __init__(self, model_name, identifier, descriptor, 
            action_url, weak_link=False, second_object_id=None, second_content_type=None):
        self.model_name = model_name
        self.identifier = identifier
        self.descriptor = descriptor
        self.action_url = action_url
        self.weak_link = weak_link
        self.second_object_id = second_object_id
        self.second_content_type = second_content_type


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
        obj_id_str = str(obj_id)
        switcher = {
                'callemail': '<a href=/internal/call_email/' + obj_id_str + '>View</a>',
                'inspection': '<a href=/internal/inspection/' + obj_id_str + '>View</a>',
                'offence': '<a href=/internal/offence/' + obj_id_str + '>View</a>',
                'sanctionoutcome': '<a href=/internal/sanction_outcome/' + obj_id_str + '>View</a>',
                'case': '<a href=/internal/case/' + obj_id_str + '>View</a>',
                }
        return switcher.get(lower_model_name, '')

def get_related_items(entity, **kwargs):
    try:
        return_list = []
        # Strong links
        for f in entity._meta.get_fields():
            if f.is_relation and f.related_model.__name__ in approved_related_item_models:

                if f.is_relation and f.one_to_many:
                    if entity._meta.model_name == 'callemail':
                        field_objects = f.related_model.objects.filter(call_email_id=entity.id)
                    elif entity._meta.model_name == 'inspection':
                        field_objects = f.related_model.objects.filter(inspection_id=entity.id)
                    elif entity._meta.model_name == 'sanctionoutcome':
                        field_objects = f.related_model.objects.filter(sanction_outcome_id=entity.id)
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
                
                elif f.is_relation:
                    field_value = f.value_from_object(entity)
                    if field_value:
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
                                )
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
                                )
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

