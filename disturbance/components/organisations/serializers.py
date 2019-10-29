from django.conf import settings
from ledger.accounts.models import EmailUser,OrganisationAddress
from disturbance.components.organisations.models import (   
                                Organisation,
                                OrganisationContact,
                                OrganisationRequest,
                                OrganisationRequestUserAction,
                                OrganisationAction,
                                OrganisationRequestLogEntry,
                                OrganisationLogEntry,
                                ledger_organisation,
                            )
from disturbance.components.organisations.utils import can_manage_org
from rest_framework import serializers
import rest_framework_gis.serializers as gis_serializers


class LedgerOrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ledger_organisation
        fields = '__all__'

class OrganisationCheckSerializer(serializers.Serializer):
    abn = serializers.CharField()
    name = serializers.CharField()

class OrganisationPinCheckSerializer(serializers.Serializer):
    pin1 = serializers.CharField()
    pin2 = serializers.CharField()

class OrganisationAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganisationAddress
        fields = (
            'id',
            'line1',
            'locality',
            'state',
            'country',
            'postcode'
        ) 

class DelegateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name')
    class Meta:
        model = EmailUser
        fields = (
            'id',
            'name',
        ) 

class OrganisationSerializer(serializers.ModelSerializer):
    address = OrganisationAddressSerializer(read_only=True) 
    pins = serializers.SerializerMethodField(read_only=True)
    delegates = DelegateSerializer(many=True,read_only=True)
    class Meta:
        model = Organisation
        fields = (
                    'id',
                    'name',
                    'abn',
                    'address',
                    'email',
                    'phone_number',
                    'pins',
                    'delegates',
                )

    def get_pins(self,obj):
        user =  self.context['request'].user
        # Check if the request user is among the first five delegates in the organisation
        if can_manage_org(obj,user):
            return {'one': obj.pin_one, 'two': obj.pin_two}
        else:
            return None

class DetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ledger_organisation
        fields = ('id','name', 'email')

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
    assigned_officer = serializers.CharField(source='assigned_officer.get_full_name', allow_null=True)
    requester = serializers.SerializerMethodField()

    def get_requester(self,obj):
        return obj.requester.get_full_name()

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

class OrganisationActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')
    class Meta:
        model = OrganisationAction 
        fields = '__all__'

class OrganisationRequestCommsSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()
    class Meta:
        model = OrganisationRequestLogEntry
        fields = '__all__'
    def get_documents(self,obj):
        return [[d.name,d._file.url] for d in obj.documents.all()]

class OrganisationCommsSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()
    class Meta:
        model = OrganisationLogEntry
        fields = '__all__'
        
    def get_documents(self,obj):
        return [[d.name,d._file.url] for d in obj.documents.all()]    

class OrganisationUnlinkUserSerializer(serializers.Serializer):
    user = serializers.IntegerField()

    def validate(self,obj):
        user = None
        try:
            user = EmailUser.objects.get(id=obj['user'])
            obj['user_obj'] = user
        except EmailUser.DoesNotExist:
            raise serializers.ValidationError('The user you want to unlink does not exist.')
        return obj
        
