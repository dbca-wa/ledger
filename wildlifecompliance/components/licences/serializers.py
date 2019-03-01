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


#    def __init__(self, *args, **kwargs):
#        # Don't pass the 'fields' arg up to the superclass
#        import ipdb; ipdb.set_trace()
#        fields = kwargs.pop('fields', None)
#
#        # Instantiate the superclass normally
#        super(DefaultPurposeSerializer, self).__init__(*args, **kwargs)

#    def get_queryset(self):
#        #import ipdb; ipdb.set_trace()
#        user = self.request.user
#		app_ids = Application.objects.filter(Q(org_applicant_id=u.id) | Q(proxy_applicant=u.id) | Q(submitter=u.id)).values_list('id', flat=True).distinct('id')
#		activity_names = ApplicationActivity.objects.filter(application_id__in=app_ids).values_list('activity_name').distinct()
#		return LicencePurpose.objects.filter(name__in=activity_names)


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


#    def qs_purpose(self):
#        #import ipdb; ipdb.set_trace()
#        user = self.request.user
#        app_ids = Application.objects.filter(Q(org_applicant_id=u.id) | Q(proxy_applicant=u.id) | Q(submitter=u.id)).values_list('id', flat=True).distinct('id')
#        activity_names = ApplicationActivity.objects.filter(application_id__in=app_ids).values_list('activity_name').distinct()
#        return LicencePurpose.objects.filter(name__in=activity_names)



class LicenceCategorySerializer(serializers.ModelSerializer):
    category_status = serializers.SerializerMethodField()
    activity = DefaultActivitySerializer(many=True, read_only=True)

    class Meta:
        model = LicenceCategory
        fields = (
            'id',
            'name',
            'short_name',
            'category_status',
            'activity'

        )

    def get_category_status(self, obj):
        return obj.get_licence_category_status_display()


class UserPurposeSerializer(serializers.ModelSerializer):
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


class UserActivitySerializer(serializers.ModelSerializer):
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
        serializer = UserPurposeSerializer(
            purpose_records,
            many=True,
        )
        return serializer.data


class UserLicenceCategorySerializer(serializers.ModelSerializer):
    category_status = serializers.SerializerMethodField()
    activity = serializers.SerializerMethodField()

    class Meta:
        model = LicenceCategory
        fields = (
            'id',
            'name',
            'short_name',
            'category_status',
            'activity'
        )

    def get_category_status(self, obj):
        return obj.get_licence_category_status_display()

    def get_activity(self, obj):
        purposes = self.context.get('purpose_records')
        activity_ids = list(purposes.values_list(
            'licence_activity_id', flat=True
        )) if purposes else []

        activities = obj.activity.filter(
            id__in=activity_ids
        ) if activity_ids else obj.activity.all()

        serializer = UserActivitySerializer(
            activities,
            many=True,
            context={
                'purpose_records': purposes
            }
        )
        return serializer.data
