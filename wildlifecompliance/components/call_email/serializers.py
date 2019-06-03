import traceback

from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometryField

from ledger.accounts.models import EmailUser
from wildlifecompliance.components.call_email.models import (
    CallEmail,
    Classification,
    ReportType,
    ComplianceFormDataRecord,
    ComplianceLogEntry,
    Location,
    ComplianceUserAction,
    MapLayer,
    ComplianceWorkflowLogEntry,)
from wildlifecompliance.components.main.serializers import CommunicationLogEntrySerializer
from rest_framework import serializers
from django.core.exceptions import ValidationError
from wildlifecompliance.components.main.fields import CustomChoiceField

from wildlifecompliance.components.users.serializers import UserAddressSerializer


class SaveEmailUserSerializer(serializers.ModelSerializer):
    residential_address = UserAddressSerializer(read_only=True)
    residential_address_id = serializers.IntegerField( required=False, write_only=True, allow_null=True)

    # residential_address = UserAddressSerializer()

    # def create(self, validated_data):
    #     return super(SaveEmailUserSerializer, self).create(validated_data)

    # def update(self, instance, validated_data):
    #     return super(SaveEmailUserSerializer, self).update(instance, validated_data)

    class Meta:
        model = EmailUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'residential_address',
            'residential_address_id',
            'phone_number',
            'mobile_number',
            'organisation',
            'dob',
        )
        read_only_fields = (
            # 'id',
            'residential_address',
        )


class EmailUserSerializer(serializers.ModelSerializer):
    residential_address = UserAddressSerializer()

    class Meta:
        model = EmailUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'residential_address',
            'phone_number',
            'mobile_number',
            'organisation',
            'dob',
        )


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


class LocationSerializerOptimized(GeoFeatureModelSerializer):
    class Meta:
        model = Location
        geo_field = 'wkb_geometry'

        fields = (
            'id',
            'wkb_geometry',
            'call_email_id',
        )


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
            #'call_email_id',
        )
        

class ReportTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReportType
        fields = (
            'id', 
            'report_type',
            'version',
        )
        read_only_fields = (
            'id', 
            'report_type',
            'version',
             )


class SaveCallEmailSerializer(serializers.ModelSerializer):
    status_display = CustomChoiceField(read_only=True)
    classification = ClassificationSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    report_type = ReportTypeSerializer(read_only=True)
    referrer = ReferrerSerializer(read_only=True)
    email_user = EmailUserSerializer(read_only=True)
    classification_id = serializers.IntegerField( required=False, write_only=True, allow_null=True)
    report_type_id = serializers.IntegerField( required=False, write_only=True, allow_null=True)
    location_id = serializers.IntegerField( required=False, write_only=True, allow_null=True)
    referrer_id = serializers.IntegerField( required=False, write_only=True, allow_null=True)
    email_user_id = serializers.IntegerField( required=False, write_only=True, allow_null=True)

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'number',
            'status',
            'status_display',
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
            'email_user',
            'email_user_id',
        )
        read_only_fields = (
            'id', 
            'status_display',
            'number', 
            'location',
            'classification',
            'report_type',
            'referrer',
            'email_user',
            )


class ReportTypeSchemaSerializer(serializers.ModelSerializer):
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


class CallEmailOptimisedSerializer(serializers.ModelSerializer):
    classification = ClassificationSerializer(read_only=True)
    location = LocationSerializerOptimized()
    report_type = ReportTypeSerializer(read_only=True)

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'location',
            'classification',
            'number',
            'report_type',
        )
        read_only_fields = ('id', )


class CallEmailSerializer(serializers.ModelSerializer):
    status_display = CustomChoiceField(read_only=True)
    classification = ClassificationSerializer(read_only=True)
    lodgement_date = serializers.CharField(source='lodged_on')
    report_type = ReportTypeSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    referrer = ReferrerSerializer(read_only=True)
    data = ComplianceFormDataRecordSerializer(many=True)
    email_user = EmailUserSerializer()

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'status_display',
            'location',
            'location_id',
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
            'referrer',
            'referrer_id',
            'advice_given',
            'advice_details',
            'email_user',
        )
        read_only_fields = (
            'id', 
            'status_display',
            )


class CallEmailDatatableSerializer(serializers.ModelSerializer):
    status_display = CustomChoiceField(read_only=True)
    classification = ClassificationSerializer(read_only=True)
    lodgement_date = serializers.CharField(source='lodged_on')
    user_is_officer = serializers.SerializerMethodField()

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'status_display',
            'user_is_officer',
            'classification',
            'classification_id',
            'lodgement_date',
            'number',
            'caller',
            'assigned_to',
        )
        read_only_fields = (
            'id', 
            'status_display',
            )

    def get_user_is_officer(self, obj):
        user = EmailUser.objects.get(id=self.context.get('request', {}).user.id)
        compliance_permissions = []
        for group in user.groups.all():
            for permission in group.permissions.all():
                compliance_permissions.append(permission.codename)
        if 'officer' in compliance_permissions:
            return True


class CreateCallEmailSerializer(serializers.ModelSerializer):
    # status_display = serializers.CharField(source='get_status_display')
    status_display = CustomChoiceField(read_only=True)
    # customer_status = CustomChoiceField(read_only=True)

    lodgement_date = serializers.CharField(
        source='lodged_on')
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
            'status',
            'status_display',
            'location_id',
            'classification_id',
            'lodgement_date',
            'caller',
            'assigned_to',
            'report_type_id',
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
            'referrer_id',
        )
        read_only_fields = (
            'id', 
            'status_display',
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


class ComplianceWorkflowLogEntrySerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()
    call_email_id = serializers.IntegerField(
        required=False, 
        write_only=True, 
        allow_null=True
    )
    region_id = serializers.IntegerField(
        required=False, 
        write_only=True, 
        allow_null=True
    )
    district_id = serializers.IntegerField(
        required=False, 
        write_only=True, 
        allow_null=True
    )

    class Meta:
        model = ComplianceWorkflowLogEntry
        fields = '__all__'

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class MapLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapLayer
        fields = (
            'display_name',
            'layer_name',
        )
