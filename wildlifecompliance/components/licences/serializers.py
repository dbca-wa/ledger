from wildlifecompliance.components.licences.models import (
    WildlifeLicence,
    LicenceCategory,
    LicenceActivity,
    LicencePurpose)
from wildlifecompliance.components.applications.serializers import BaseApplicationSerializer
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
            'licence_document',
            'replaced_by',
            'current_application',
            'extracted_fields',
            'last_issue_date',
        )

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
    purpose_in_current_licence = serializers.SerializerMethodField(read_only=True)

    class Meta:
        # list_serializer_class = UserActivityExcludeSerializer
        model = LicencePurpose
        fields = (
            'id',
            'name',
            'base_application_fee',
            'base_licence_fee',
            'short_name',
            'purpose_in_current_licence'
        )

    def get_purpose_in_current_licence(self, obj):
        # TODO: 1. need to get a list of all licences for org (if org) or proxy (if proxy) or user
        # TODO: 2. get list of purposes of currently issued licences
        # user_id = self.context['request'].user.id
        # licence_ids = WildlifeLicence.objects.filter()
        # current_purpose_ids =
        # if obj.id in current_purpose_ids:
        #     return True
        return False


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
