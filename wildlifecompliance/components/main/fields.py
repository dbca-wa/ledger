import json
from rest_framework import serializers


class CustomChoiceField(serializers.Field):

    def to_representation(self, obj):
        field = self.parent.Meta.model._meta.get_field(self.field_name)
        data = {'id': obj, 'name': ''}
        for choice in field.choices:
            if choice[0] == obj:
                data['name'] = choice[1]
                break

        return data

    def to_internal_value(self, data):
        try:
            return json.loads(data)['id']
        except KeyError:
            return data
