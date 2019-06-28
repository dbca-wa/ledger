from wildlifecompliance.components.licences.models import (
    WildlifeLicence,
    LicenceCategory,
    LicenceActivity,
    LicencePurpose
)
from wildlifecompliance.components.applications.serializers import (
    WildlifeLicenceApplicationSerializer,
    ExternalApplicationSelectedActivityMergedSerializer
)
from rest_framework import serializers


class WildlifeLicenceCanActionSerializer(serializers.Serializer):
    """
    Custom serializer for WildlifeLicence.can_action DICT object for each action
    """
    # can_renew = serializers.BooleanField(read_only=True)
    # can_amend = serializers.BooleanField(read_only=True)
    # can_surrender = serializers.BooleanField(read_only=True)
    # can_cancel = serializers.BooleanField(read_only=True)
    # can_suspend = serializers.BooleanField(read_only=True)
    # can_reissue = serializers.BooleanField(read_only=True)
    # can_reinstate = serializers.BooleanField(read_only=True)
    #
    # class Meta:
    #     fields = (
    #         'can_renew',
    #         'can_amend',
    #         'can_surrender',
    #         'can_cancel',
    #         'can_suspend',
    #         'can_reissue',
    #         'can_reinstate',
    #     )
    #     # the serverSide functionality of datatables is such that only columns that have field 'data'
    #     # defined are requested from the serializer. Use datatables_always_serialize to force render
    #     # of fields that are not listed as 'data' in the datatable columns
    #     datatables_always_serialize = fields
    def to_representation(self, obj):
        print(obj)
        return ''

class WildlifeLicenceSerializer(serializers.ModelSerializer):
    licence_document = serializers.CharField(
        source='licence_document._file.url')
    current_application = WildlifeLicenceApplicationSerializer(read_only=True)
    last_issue_date = serializers.SerializerMethodField(read_only=True)
    licence_number = serializers.SerializerMethodField(read_only=True)

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
        return obj.latest_activities.first().issue_date if obj.latest_activities else ''

    def get_licence_number(self, obj):
        return obj.reference


class DTInternalWildlifeLicenceSerializer(WildlifeLicenceSerializer):
    licence_document = serializers.CharField(
        source='licence_document._file.url')
    current_application = WildlifeLicenceApplicationSerializer(read_only=True)
    last_issue_date = serializers.SerializerMethodField(read_only=True)
    latest_activities_merged = ExternalApplicationSelectedActivityMergedSerializer(many=True, read_only=True)
    # can_action = WildlifeLicenceCanActionSerializer(read_only=True)
    can_action = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WildlifeLicence
        fields = (
            'id',
            'licence_number',
            'licence_document',
            'current_application',
            'last_issue_date',
            'latest_activities_merged',
            'is_latest_in_category',
            'can_action',
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields

    def get_last_issue_date(self, obj):
        return obj.latest_activities.first().issue_date if obj.latest_activities else ''

    def get_can_action(self, obj):
        # set default but use to_representation to calculate based on latest_activities_merged.can_action
        can_action = {
            'can_amend': False,
            'can_renew': False,
            'can_reactivate_renew': False,
            'can_surrender': False,
            'can_cancel': False,
            'can_suspend': False,
            'can_reissue': False,
            'can_reinstate': False,
        }
        return can_action

    def to_representation(self, obj):
        data = super(DTInternalWildlifeLicenceSerializer, self).to_representation(obj)
        print('\n\nLICENCE')

        latest_activities_merged = data['latest_activities_merged']

        # only check if licence is the latest in its category for the applicant
        if data['is_latest_in_category']:
            print('is latest in category, licence can_action')
            # set True if any activities can be actioned
            for activity in latest_activities_merged:
                activity_can_action = activity.get('can_action')
                if activity_can_action.get('can_amend'):
                    data.get('can_action')['can_amend'] = True
                if activity_can_action.get('can_renew'):
                    data.get('can_action')['can_renew'] = True
                if activity_can_action.get('can_reactivate_renew'):
                    data.get('can_action')['can_reactivate_renew'] = True
                if activity_can_action.get('can_surrender'):
                    data.get('can_action')['can_surrender'] = True
                if activity_can_action.get('can_cancel'):
                    data.get('can_action')['can_cancel'] = True
                if activity_can_action.get('can_suspend'):
                    data.get('can_action')['can_suspend'] = True
                if activity_can_action.get('can_reissue'):
                    data.get('can_action')['can_reissue'] = True
                if activity_can_action.get('can_reinstate'):
                    data.get('can_action')['can_reinstate'] = True

        # data.update({'can_action':'noooooooo'})
        print('final licence data')
        print(data)
        return data


class DTExternalWildlifeLicenceSerializer(WildlifeLicenceSerializer):
    licence_document = serializers.CharField(
        source='licence_document._file.url')
    current_application = WildlifeLicenceApplicationSerializer(read_only=True)
    last_issue_date = serializers.SerializerMethodField(read_only=True)
    latest_activities_merged = ExternalApplicationSelectedActivityMergedSerializer(many=True, read_only=True)
    can_action = WildlifeLicenceCanActionSerializer(read_only=True)

    class Meta:
        model = WildlifeLicence
        fields = (
            'id',
            'licence_number',
            'licence_document',
            'current_application',
            'last_issue_date',
            'latest_activities_merged',
            'is_latest_in_category',
            'can_action',
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields

    def get_last_issue_date(self, obj):
        return obj.latest_activities.first().issue_date if obj.latest_activities else ''


class BasePurposeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = LicencePurpose
        fields = (
            'id',
            'name',
            'short_name',
        )


class DefaultPurposeSerializer(BasePurposeSerializer):
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

    class Meta:
        model = LicenceActivity
        fields = (
            'id',
            'name',
            'activity',
            'short_name',
            'not_for_organisation'
        )


class PurposeSerializer(BasePurposeSerializer):
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
            purpose_records.filter(
                licence_activity_id=obj.id
            ),
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

        # If purpose_records context is set but is empty, force display of zero activities
        # otherwise, assume we want to retrieve all activities for the Licence Category
        if self.context.has_key('purpose_records'):
            activities = obj.activity.filter(
                id__in=activity_ids
            )
        else:
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
