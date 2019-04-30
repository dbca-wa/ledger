from wildlifecompliance.components.licences.models import (
    WildlifeLicence,
    LicenceCategory,
    LicenceActivity,
    LicencePurpose
)
from wildlifecompliance.components.applications.serializers import (
    BaseApplicationSerializer,
    DTInternalApplicationSerializer,
    DTExternalApplicationSerializer
)
from rest_framework import serializers


class WildlifeLicenceSerializer(serializers.ModelSerializer):
    licence_document = serializers.CharField(
        source='licence_document._file.url')
    current_application = BaseApplicationSerializer(read_only=True)
    last_issue_date = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WildlifeLicence
        fields = (
            'id',
            'licence_number',
            'licence_document',
            'replaced_by',
            'current_application',
            'extracted_fields',
            'last_issue_date',
        )

    def get_last_issue_date(self, obj):
        return obj.current_activities.order_by('-issue_date').first().issue_date


class DTInternalWildlifeLicenceSerializer(WildlifeLicenceSerializer):
    licence_document = serializers.CharField(
        source='licence_document._file.url')
    current_application = DTInternalApplicationSerializer(read_only=True)
    last_issue_date = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WildlifeLicence
        fields = (
            'id',
            'licence_number',
            'licence_document',
            'current_application',
            'last_issue_date',
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields

    def get_last_issue_date(self, obj):
        return obj.current_activities.order_by('-issue_date').first().issue_date


class DTExternalWildlifeLicenceSerializer(WildlifeLicenceSerializer):
    licence_document = serializers.CharField(
        source='licence_document._file.url')
    current_application = DTExternalApplicationSerializer(read_only=True)
    last_issue_date = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WildlifeLicence
        fields = (
            'id',
            'licence_number',
            'licence_document',
            'current_application',
            'last_issue_date',
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields

    def get_last_issue_date(self, obj):
        return obj.current_activities.order_by('-issue_date').first().issue_date


class DefaultPurposeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = LicencePurpose
        fields = (
            'id',
            'name',
            'base_application_fee',
            'base_licence_fee',
            'short_name'
        )


class DefaultActivitySerializer(serializers.ModelSerializer):

    name = serializers.CharField()
    activity = DefaultPurposeSerializer(many=True, read_only=True)
    #activity = DefaultPurposeSerializer(many=True,read_only=True, queryset=self.qs_purpose())
    class Meta:
        model = LicenceActivity
        fields = (
            'id',
            'name',
            'activity',
            'short_name',
            'not_for_organisation'
        )


class PurposeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = LicencePurpose
        fields = (
            'id',
            'name',
            'base_application_fee',
            'base_licence_fee',
            'short_name',
        )


class ActivitySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    purpose = serializers.SerializerMethodField()

    class Meta:
        model = LicenceActivity
        fields = (
            'id',
            'name',
            'purpose',
            'short_name',
            'not_for_organisation'
        )

    def get_purpose(self, obj):
        purposes = self.context.get('purpose_records')
        purpose_records = purposes if purposes else obj.purpose.all()
        serializer = PurposeSerializer(
            purpose_records,
            many=True,
        )
        return serializer.data


class LicenceCategorySerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField()

    class Meta:
        model = LicenceCategory
        fields = (
            'id',
            'name',
            'short_name',
            'activity'
        )

    def get_activity(self, obj):
        purposes = self.context.get('purpose_records')
        activity_ids = list(purposes.values_list(
            'licence_activity_id', flat=True
        )) if purposes else []

        activities = obj.activity.filter(
            id__in=activity_ids
        ) if activity_ids else obj.activity.all()

        serializer = ActivitySerializer(
            activities,
            many=True,
            context={
                'purpose_records': purposes
            }
        )
        return serializer.data
