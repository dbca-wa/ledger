from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from disturbance.components.organisations.models import (   
                                Organisation,
                                OrganisationContact,
                                OrganisationRequest,
                                OrganisationRequestUserAction,
                                OrganisationRequestLogEntry,
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

class OrgRequestRequesterSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = EmailUser
        fields = (
                'email',
                'mobile_number',
                'phone_number',
                'full_name'
                )

    def get_full_name(self, obj):
        return obj.get_full_name()

class OrganisationRequestSerializer(serializers.ModelSerializer):
    identification = serializers.FileField()
    requester = OrgRequestRequesterSerializer(read_only=True)
    status = serializers.SerializerMethodField()
    class Meta:
        model = OrganisationRequest
        fields = '__all__'
        read_only_fields = ('requester','lodgement_date','assigned_officer')

    def get_status(self,obj):
        return obj.get_status_display()

class OrganisationRequestDTSerializer(OrganisationRequestSerializer):
    requester = serializers.SerializerMethodField()

    def get_requester(self,obj):
        return obj.requester.get_full_name()

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class UserOrganisationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='organisation.name')
    abn = serializers.CharField(source='organisation.abn')
    class Meta:
        model = Organisation
        fields = (
            'id',
            'name',
            'abn'
        )

class OrganisationRequestActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')
    class Meta:
        model = OrganisationRequestUserAction 
        fields = '__all__'

class OrganisationRequestCommsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationRequestLogEntry
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    disturbance_organisations = UserOrganisationSerializer(many=True)
    residential_address = AddressSerializer()
    personal_details = serializers.SerializerMethodField()
    address_details = serializers.SerializerMethodField()
    contact_details = serializers.SerializerMethodField()
    class Meta:
        model = EmailUser
        fields = (
            'id',
            'last_name',
            'first_name',
            'email',
            'residential_address',
            'phone_number',
            'mobile_number',
            'disturbance_organisations',
            'personal_details',
            'address_details',
            'contact_details'
        )
    
    def get_personal_details(self,obj):
        return True if obj.last_name  and obj.first_name else False

    def get_address_details(self,obj):
        return True if obj.residential_address else False

    def get_contact_details(self,obj):
        if obj.mobile_number and obj.email:
            return True
        elif obj.mobile_number and obj.phone_number:
            return True
        else:
            return False
