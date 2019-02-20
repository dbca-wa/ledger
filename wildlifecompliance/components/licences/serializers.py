from wildlifecompliance.components.licences.models import (
    WildlifeLicence,
    WildlifeLicenceClass,
    WildlifeLicenceActivityType,
    WildlifeLicenceActivity)
from wildlifecompliance.components.applications.serializers import BaseApplicationSerializer
from rest_framework import serializers


class WildlifeLicenceSerializer(serializers.ModelSerializer):
    licence_document = serializers.CharField(
        source='licence_document._file.url')
    status = serializers.CharField(source='get_status_display')
    current_application = BaseApplicationSerializer(read_only=True)

    class Meta:
        model = WildlifeLicence
        fields = (
            'id',
            'licence_document',
            'replaced_by',
            'current_application',
            'activity',
            'region',
            'tenure',
            'title',
            'renewal_sent',
            'issue_date',
            'original_issue_date',
            'start_date',
            'expiry_date',
            'surrender_details',
            'suspension_details',
            'extracted_fields',
            'status'
        )


class DefaultActivitySerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = WildlifeLicenceActivity
        fields = (
            'id',
            'name',
            'base_application_fee',
            'base_licence_fee',
            'short_name'
        )


class DefaultActivityTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    activity = DefaultActivitySerializer(many=True, read_only=True)

    class Meta:
        model = WildlifeLicenceActivityType
        fields = (
            'id',
            'name',
            'activity',
            'short_name',
            'not_for_organisation'
        )



class WildlifeLicenceClassSerializer(serializers.ModelSerializer):
    class_status = serializers.SerializerMethodField()
    activity_type = DefaultActivityTypeSerializer(many=True, read_only=True)

    class Meta:
        model = WildlifeLicenceClass
        fields = (
            'id',
            'name',
            'short_name',
            'class_status',
            'activity_type'

        )

    def get_class_status(self, obj):
        return obj.get_licence_class_status_display()


class UserActivitySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    purpose_in_current_licence = serializers.SerializerMethodField(read_only=True)

    class Meta:
        # list_serializer_class = UserActivityExcludeSerializer
        model = WildlifeLicenceActivity
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


class UserActivityTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    activity = UserActivitySerializer(many=True, read_only=True)

    class Meta:
        model = WildlifeLicenceActivityType
        fields = (
            'id',
            'name',
            'activity',
            'short_name',
            'not_for_organisation'
        )


class UserWildlifeLicenceClassSerializer(serializers.ModelSerializer):
    class_status = serializers.SerializerMethodField()
    activity_type = UserActivityTypeSerializer(many=True, read_only=True)

    class Meta:
        model = WildlifeLicenceClass
        fields = (
            'id',
            'name',
            'short_name',
            'class_status',
            'activity_type'
        )

    def get_class_status(self, obj):
        return obj.get_licence_class_status_display()