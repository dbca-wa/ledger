import traceback

from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometryField

from wildlifecompliance.components.call_email.models import (
    CallEmail,
    Classification,
    ReportType,
    ComplianceFormDataRecord,
    ComplianceLogEntry,
    Location,
    ComplianceUserAction,
)
from wildlifecompliance.components.main.serializers import CommunicationLogEntrySerializer
from rest_framework import serializers
from django.core.exceptions import ValidationError


class ComplianceFormDataRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceFormDataRecord
        fields = (
            'field_name',
            'schema_name',
            'component_type',
            'instance_name',
            'comment',
            'deficiency',
            'value',
        )
        read_only_fields = (
            'field_name',
            'schema_name',
            'component_type',
            'instance_name',
            'comment',
            'deficiency',
            'value',
        )


class ClassificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Classification
        fields = (
            'id',
            'name',
        )
        read_only_fields = ('id', 'name', )


class CreateCallEmailSerializer(serializers.ModelSerializer):
    data = ComplianceFormDataRecordSerializer(many=True)

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'classification',
            'number',
            'caller',
            'assigned_to',
            'data',
        )
        read_only_fields = ('id', )


class ReportTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportType
        fields = (
            'report_type',
            'schema',
        )
        read_only_fields = ('report_type', 'schema')


class LocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Location
        geo_field = 'wkb_geometry'
        fields = (
            'id',
            'street',
            'town_suburb',
            'state',
            'postcode',
            'country',
            'wkb_geometry',
        )

    # def update(self, request, validated_data):
    #     print("location serializer update")
    #     # print(validated_data.pop('location'))
    #     print("serializer.validated_data")
    #     print(validated_data)
    #     location_data = validated_data.pop('location')
    #     updated_location, created = Location.objects.get_or_create(**location_data)
                
    #     print("location_data")
    #     print(location_data)
    #     call_email, created = CallEmail.objects.get_or_create(location_call=updated_location, **validated_data)
    #     print("call_email")
    #     print(call_email)
        
    #     return call_email

class CallEmailSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    classification = ClassificationSerializer(read_only=True)
    lodgement_date = serializers.CharField(
        source='lodged_on')
    report_type = ReportTypeSerializer()
    location = LocationSerializer()
    data = ComplianceFormDataRecordSerializer(many=True)

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'location',
            'classification',
            'classification_id',
            'schema',
            'lodgement_date',
            'number',
            'caller',
            'assigned_to',
            'report_type',
            'data',
            'location',
        )
        read_only_fields = ('id', )


class UpdateCallEmailSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    #location_id = serializers.IntegerField(
     #   required=False, write_only=True)
    classification = ClassificationSerializer(read_only=True)
    classification_id = serializers.IntegerField(
        required=False, write_only=True)

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'classification',
            'classification_id',
            'location',
            'number',
            'caller',
            'assigned_to',
            'location',
        )
        read_only_fields = ('id', )
    
    def update(self, request, validated_data):
        print("location serializer update")
        # print(validated_data.pop('location'))
        print("serializer.validated_data")
        print(validated_data)
        location_data = validated_data.pop('location')
        print("location_data")
        print(location_data)
        updated_location, created = Location.objects.get_or_create(**location_data)
        # call_email, created = CallEmail.objects.update(**validated_data)
        # call_email, created = CallEmail.objects.get_or_create(location=updated_location, **validated_data)
        call_email = CallEmail.objects.get(id=id)
        print("call_email.location")
        print(call_email.location)
        # updated_location, created = Location.objects.update(location_call=call_email, **location_data)
        # call_email.save()
        return call_email
        

class UpdateRendererDataSerializer(CallEmailSerializer):
    data = ComplianceFormDataRecordSerializer(many=True)

    class Meta:
        model = CallEmail
        fields = (
            'schema',
            'data',
        )


class ComplianceUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')

    class Meta:
        model = ComplianceUserAction
        fields = '__all__'


class ComplianceLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceLogEntry
        fields = '__all__'
        read_only_fields = (
            'customer',
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]
