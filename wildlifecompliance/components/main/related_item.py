import traceback
from django.contrib.contenttypes.models import ContentType
from wildlifecompliance.components.main.models import WeakLinks
from serializers import RelatedItemsSerializer
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer
from django.core.exceptions import ValidationError


class RelatedItem:
    # list of approved related item models
    approved_related_item_models = [
            'Offence',
            'CallEmail',
            'Inspection',
            'SanctionOutcome',
            'Case',
            ]

    def __init__(self):
        self.model_name = ''
        self.identifier = ''
        self.descriptor = ''
        self.action_url = ''
        self.link_type = ''
        self.second_object_id = None
        self.second_content_type = None

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
            related_item = RelatedItem()
            if f.is_relation and f.related_model.__name__ in related_item.approved_related_item_models:
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
                        related_item.model_name = format_model_name(f.related_model.__name__)
                        related_item.identifier = field_object.get_related_items_identifier
                        related_item.descriptor = field_object.get_related_items_descriptor
                        related_item.action_url = format_url(
                                model_name=f.related_model.__name__, 
                                obj_id=field_object.id
                                )
                        related_item.link_type = 'strong'
                        return_list.append(related_item)
                
                elif f.is_relation:
                    field_value = f.value_from_object(entity)
                    if field_value:
                        field_object = f.related_model.objects.get(id=field_value)
                        related_item.model_name = format_model_name(f.name)
                        related_item.identifier = field_object.get_related_items_identifier
                        related_item.descriptor = field_object.get_related_items_descriptor
                        related_item.action_url = format_url(
                                model_name=f.related_model.__name__, 
                                obj_id=field_object.id
                                )
                        related_item.link_type =  'strong'
                        return_list.append(related_item)

        # Weak links - first pass with instance as first_content_object
        entity_content_type = ContentType.objects.get_for_model(type(entity))

        weak_links = WeakLinks.objects.filter(
                first_content_type__pk=entity_content_type.id,
                first_object_id=entity.id
                )
        for link in weak_links:
            related_item = RelatedItem()
            link_content_type = ContentType.objects.get_for_model(
                    type(
                        link.second_content_object
                        ))
            related_item.model_name =  format_model_name(link_content_type.model)
            related_item.identifier = link.second_content_object.get_related_items_identifier
            related_item.descriptor = link.second_content_object.get_related_items_descriptor
            related_item.second_object_id = link.second_content_object.id
            related_item.second_content_type = link_content_type.model
            related_item.link_type = 'weak'
            return_list.append(related_item)

        # Weak links - first pass with instance as second_content_object
        weak_links = WeakLinks.objects.filter(
                second_content_type__pk=entity_content_type.id,
                second_object_id=entity.id
                )
        for link in weak_links:
            related_item = RelatedItem()
            link_content_type = ContentType.objects.get_for_model(
                    type(
                        link.first_content_object
                        ))
            related_item.model_name = format_model_name(link_content_type.model)
            related_item.identifier = link.first_content_object.get_related_items_identifier
            related_item.descriptor = link.first_content_object.get_related_items_descriptor
            related_item.second_object_id = link.first_content_object.id
            related_item.second_content_type = link_content_type.model
            related_item.link_type = 'weak'
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

