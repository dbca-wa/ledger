import json
from django.core.exceptions import FieldDoesNotExist
from rest_framework import serializers


class CustomChoiceField(serializers.Field):

    def __init__(self, **kwargs):
        self.choices = kwargs.pop('choices', None)
        super(CustomChoiceField, self).__init__(**kwargs)

    def to_representation(self, obj):
        try:
            field = self.parent.Meta.model._meta.get_field(self.field_name)
            # Allow manual choice overrides for the existing model fields
            choices = self.choices if self.choices else field.choices
        except FieldDoesNotExist:
            # If it's a computed/missing field - rely on manually supplied choices
            choices = self.choices
        data = {'id': obj, 'name': ''}
        for choice in choices:
            if choice[0] == obj:
                data['name'] = choice[1]
                break

        return data

    def to_internal_value(self, data):
        try:
            return json.loads(data)['id']
        except (KeyError, ValueError) as exc:
            return data
