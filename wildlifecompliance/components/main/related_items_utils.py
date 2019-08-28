# related_items.py stores related item and WeakLinks utility functions

from django.contrib.contenttypes.models import ContentType
from wildlifecompliance.components.main.models import WeakLinks

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
                'callemail': '<a href=' + '/internal/call_email/{}'.format(obj_id) + '>View</a>',
                'inspection': '<a href=' + '/internal/inspection/{}'.format(obj_id) + '>View</a>',
                'offence': '<a href=' + '/internal/offence/{}'.format(obj_id) + '>View</a>',
                'sanctionoutcome': '<a href=' + '/internal/sanction_outcome/{}'.format(obj_id) + '>View</a>',
                'case': '<a href=' + '/internal/case/{}'.format(obj_id) + '>View</a>',
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
# End examples

