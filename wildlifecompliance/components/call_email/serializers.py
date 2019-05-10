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


class ReferrerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Classification
        fields = (
            'id',
            'name',
        )
        read_only_fields = ('id', 'name', )


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
            'details',
        )
        

class ReportTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportType
        fields = (
            'id', 
            'report_type',
            'version',
            #'schema',
        )
        read_only_fields = (
            'id', 
            'report_type',
            'version',
            #'schema',
             )


class SaveCallEmailSerializer(serializers.ModelSerializer):
    classification = ClassificationSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    report_type = ReportTypeSerializer(read_only=True)
    referrer = ReferrerSerializer(read_only=True)
    classification_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)
    report_type_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)        
    location_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)        
    referrer_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)        

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'number',
            #'status',
            'schema',
            'location',
            'classification',
            'report_type',
            'location_id',
            'classification_id',
            'report_type_id',
            'caller',
            'assigned_to',
            'referrer_id',
            'referrer',
            'caller_phone_number',
            'anonymous_call',
            'caller_wishes_to_remain_anonymous',
            'occurrence_from_to',
            'occurrence_date_from',
            'occurrence_time_from',
            'occurrence_date_to',
            'occurrence_time_to',
            'advice_given',
            'advice_details',
        )
        read_only_fields = (
            'id', 
            'number', 
            'location',
            'classification',
            'report_type',
            'referrer',
            )


class UpdateSchemaSerializer(serializers.ModelSerializer):
    report_type_id = serializers.IntegerField(
        required=False, write_only=True, allow_null=True)        

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'schema',
            'report_type_id',
        )
        read_only_fields = (
            'id', 
            )


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
            'report_type_id',
            'data',
            'caller_phone_number',
            'anonymous_call',
            'caller_wishes_to_remain_anonymous',
            'occurrence_from_to',
            'occurrence_date_from',
            'occurrence_time_from',
            'occurrence_date_to',
            'occurrence_time_to',
            'advice_given',
            'advice_details',
        )
        read_only_fields = ('id', )


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
