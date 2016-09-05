from rest_framework import serializers

from wildlifelicensing.apps.main.models import WildlifeLicenceType
from wildlifelicensing.apps.returns.models import ReturnType


class LicenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WildlifeLicenceType
        fields = ('display_name', 'code')


class ResourceSerializer(serializers.Serializer):
    name = serializers.ReadOnlyField()
    schema = serializers.ReadOnlyField()


class ReturnTypeSerializer(serializers.ModelSerializer):
    licence_type = LicenceTypeSerializer()
    resources = ResourceSerializer(many=True)

    class Meta:
        model = ReturnType
        fields = ('id', 'licence_type', 'resources')
