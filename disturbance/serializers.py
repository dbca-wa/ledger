from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from disturbance.models import (   Organisation,
                                OrganisationContact,
                                OrganisationRequest
                            )
from rest_framework import serializers
import rest_framework_gis.serializers as gis_serializers


class OrganisationCheckSerializer(serializers.Serializer):
    abn = serializers.CharField()
    name = serializers.CharField()

class OrganisationPinCheckSerializer(serializers.Serializer):
    pin1 = serializers.CharField()
    pin2 = serializers.CharField()

class OrganisationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Organisation
        fields = '__all__'

class OrganisationContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationContact
        fields = '__all__'

class OrganisationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationRequest
        fields = '__all__'
