from ledger.accounts.models import EmailUser
# from wildlifecompliance.components.applications.utils import amendment_requests
from wildlifecompliance.components.applications.models import (
    Application,
    ApplicationUserAction,
    ApplicationLogEntry,
    ApplicationCondition,
    ApplicationStandardCondition,
    Assessment,
    ActivityPermissionGroup,
    AmendmentRequest,
    ApplicationSelectedActivity,
    ApplicationFormDataRecord,
)
from wildlifecompliance.components.organisations.models import (
    Organisation
)
from wildlifecompliance.components.licences.models import LicenceActivity
from wildlifecompliance.components.main.serializers import CommunicationLogEntrySerializer
from wildlifecompliance.components.organisations.serializers import (
    OrganisationSerializer,
    ExternalOrganisationSerializer
)
from wildlifecompliance.components.users.serializers import UserAddressSerializer, DocumentSerializer
from wildlifecompliance.components.main.fields import CustomChoiceField
from wildlifecompliance import helpers

from rest_framework import serializers


class ApplicationSelectedActivityCanActionSerializer(serializers.Serializer):
    """
    Custom serializer for ApplicationSelectedActivity.can_action DICT object for each action
    """
    licence_activity_id = serializers.IntegerField(read_only=True)
    can_renew = serializers.BooleanField(read_only=True)
    can_amend = serializers.BooleanField(read_only=True)
    can_surrender = serializers.BooleanField(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    can_suspend = serializers.BooleanField(read_only=True)
    can_reissue = serializers.SerializerMethodField(read_only=True)
    can_reinstate = serializers.BooleanField(read_only=True)

    class Meta:
        fields = (
            'licence_activity_id',
            'can_renew',
            'can_amend',
            'can_surrender',
            'can_cancel',
            'can_suspend',
            'can_reissue',
            'can_reinstate',
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields

    def get_can_reissue(self, obj):
        try:
            user = self.context['request'].user
        except (KeyError, AttributeError):
            return False
        if user is None:
            return False
        return (user.has_perm('wildlifecompliance.system_administrator') or
            user.has_wildlifelicenceactivity_perm([
                'issuing_officer',
            ], obj.get('licence_activity_id'))) and obj.get('can_reissue')


class ApplicationSelectedActivitySerializer(serializers.ModelSerializer):
    activity_name_str = serializers.SerializerMethodField(read_only=True)
    issue_date = serializers.SerializerMethodField(read_only=True)
    start_date = serializers.SerializerMethodField(read_only=True)
    expiry_date = serializers.SerializerMethodField(read_only=True)
    approve_options = serializers.SerializerMethodField(read_only=True)
    purposes = serializers.SerializerMethodField(read_only=True)
    activity_purpose_names = serializers.SerializerMethodField(read_only=True)
    processing_status = CustomChoiceField(read_only=True)
    activity_status = CustomChoiceField(read_only=True)
    can_action = ApplicationSelectedActivityCanActionSerializer(read_only=True)
    licence_fee = serializers.DecimalField(
        max_digits=8, decimal_places=2, coerce_to_string=False, read_only=True),
    payment_status = serializers.CharField(read_only=True)
    can_pay_licence_fee = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationSelectedActivity
        fields = '__all__'

    def get_activity_name_str(self, obj):
        return obj.licence_activity.name if obj.licence_activity else ''

    def get_issue_date(self, obj):
        return obj.issue_date.strftime('%d/%m/%Y %H:%M') if obj.issue_date else ''

    def get_start_date(self, obj):
        return obj.start_date.strftime('%Y-%m-%d') if obj.start_date else ''

    def get_expiry_date(self, obj):
        return obj.expiry_date.strftime('%Y-%m-%d') if obj.expiry_date else ''

    def get_approve_options(self, obj):
        return [{'label': 'Approved', 'value': 'approved'}, {'label': 'Declined', 'value': 'declined'}]

    def get_purposes(self, obj):
        from wildlifecompliance.components.licences.serializers import PurposeSerializer
        return PurposeSerializer(obj.purposes, many=True).data

    def get_activity_purpose_names(self, obj):
        return ','.join([p.name for p in obj.purposes])

    def get_can_pay_licence_fee(self, obj):
        return not obj.licence_fee_paid and obj.processing_status == ApplicationSelectedActivity.PROCESSING_STATUS_AWAITING_LICENCE_FEE_PAYMENT


class ExternalApplicationSelectedActivitySerializer(serializers.ModelSerializer):
    activity_name_str = serializers.SerializerMethodField(read_only=True)
    issue_date = serializers.SerializerMethodField(read_only=True)
    start_date = serializers.SerializerMethodField(read_only=True)
    expiry_date = serializers.SerializerMethodField(read_only=True)
    activity_purpose_names = serializers.SerializerMethodField(read_only=True)
    activity_status = CustomChoiceField(read_only=True)
    can_action = ApplicationSelectedActivityCanActionSerializer(read_only=True)
    can_pay_licence_fee = serializers.SerializerMethodField()
    licence_fee = serializers.DecimalField(
        max_digits=8, decimal_places=2, coerce_to_string=False, read_only=True)
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = ApplicationSelectedActivity
        fields = (
            'id',
            'activity_name_str',
            'issue_date',
            'start_date',
            'expiry_date',
            'activity_purpose_names',
            'activity_status',
            'can_action',
            'licence_fee',
            'payment_status',
            'can_pay_licence_fee',
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields

    def get_activity_name_str(self, obj):
        return obj.licence_activity.name if obj.licence_activity else ''

    def get_issue_date(self, obj):
        return obj.issue_date.strftime('%d/%m/%Y') if obj.issue_date else ''

    def get_start_date(self, obj):
        return obj.start_date.strftime('%d/%m/%Y') if obj.start_date else ''

    def get_expiry_date(self, obj):
        return obj.expiry_date.strftime('%d/%m/%Y') if obj.expiry_date else ''

    def get_activity_purpose_names(self, obj):
        return ','.join([p.name for p in obj.purposes])

    def get_can_pay_licence_fee(self, obj):
        return not obj.licence_fee_paid and obj.processing_status == ApplicationSelectedActivity.PROCESSING_STATUS_AWAITING_LICENCE_FEE_PAYMENT


class ExternalApplicationSelectedActivityMergedSerializer(serializers.Serializer):
    """
    Custom serializer for WildlifeLicence.latest_activities_merged LIST of DICT objects for each
    ApplicationSelectedActivity, therefore use of obj.get('fieldname') to retrieve data in SerializerMethodFields
    """
    licence_activity_id = serializers.IntegerField(read_only=True)
    activity_name_str = serializers.CharField(read_only=True)
    issue_date = serializers.SerializerMethodField(read_only=True)
    start_date = serializers.SerializerMethodField(read_only=True)
    expiry_date = serializers.SerializerMethodField(read_only=True)
    activity_purpose_names_and_status = serializers.CharField(read_only=True)
    can_action = ApplicationSelectedActivityCanActionSerializer(read_only=True)

    class Meta:
        fields = (
            'licence_activity_id',
            'activity_name_str',
            'issue_date',
            'start_date',
            'expiry_date',
            'activity_purpose_names_and_status',
            'can_action',
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields

    def get_issue_date(self, obj):
        return obj.get('issue_date').strftime('%d/%m/%Y') if obj.get('issue_date') else ''

    def get_start_date(self, obj):
        return obj.get('start_date').strftime('%d/%m/%Y') if obj.get('start_date') else ''

    def get_expiry_date(self, obj):
        return obj.get('expiry_date').strftime('%d/%m/%Y') if obj.get('expiry_date') else ''


class EmailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'title',
            'organisation')


class EmailUserAppViewSerializer(serializers.ModelSerializer):
    residential_address = UserAddressSerializer()
    identification = DocumentSerializer()

    class Meta:
        model = EmailUser
        fields = ('id',
                  'email',
                  'first_name',
                  'last_name',
                  'dob',
                  'title',
                  'organisation',
                  'residential_address',
                  'identification',
                  'email',
                  'phone_number',
                  'mobile_number',)


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = LicenceActivity
        fields = ('id', 'name', 'short_name')


class ActivityPermissionGroupSerializer(serializers.ModelSerializer):
    licence_activities = ActivitySerializer(many=True)

    class Meta:
        model = ActivityPermissionGroup
        fields = (
            'id',
            'name',
            'display_name',
            'licence_activities')


class AssessmentSerializer(serializers.ModelSerializer):
    assessor_group = ActivityPermissionGroupSerializer(read_only=True)
    status = CustomChoiceField(read_only=True)
    inspection_report = serializers.FileField()

    class Meta:
        model = Assessment
        fields = (
            'id',
            'application',
            'assessor_group',
            'date_last_reminded',
            'status',
            'licence_activity',
            'inspection_comment',
            'final_comment',
            'inspection_date',
            'inspection_report',
            'is_inspection_required',
        )


class SimpleSaveAssessmentSerializer(serializers.ModelSerializer):
    inspection_report = serializers.FileField()

    class Meta:
        model = Assessment
        fields = (
            'inspection_comment',
            'final_comment',
            'inspection_date',
            'inspection_report',
            'is_inspection_required',
            )


class SaveAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = (
            'assessor_group',
            'application',
            'text',
            'licence_activity')

    def validate(self, data):
        licence_activity = data.get('licence_activity')
        assessor_group = data.get('assessor_group')
        if not licence_activity:
            raise serializers.ValidationError("No licence activity supplied!")

        group_match = ActivityPermissionGroup.get_groups_for_activities(
            licence_activity, 'assessor').filter(id=assessor_group.id).first()
        if not group_match:
            raise serializers.ValidationError("Invalid group (ID: %s) selected to assess activity ID: %s" % (
                assessor_group, licence_activity))

        return data


class AmendmentRequestSerializer(serializers.ModelSerializer):
    reason = CustomChoiceField()

    class Meta:
        model = AmendmentRequest
        fields = '__all__'


class ExternalAmendmentRequestSerializer(serializers.ModelSerializer):
    reason = CustomChoiceField(read_only=True)
    licence_activity = ActivitySerializer(read_only=True)

    class Meta:
        model = AmendmentRequest
        fields = '__all__'


class ApplicationFormDataRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationFormDataRecord
        fields = (
            'field_name',
            'schema_name',
            'component_type',
            'instance_name',
            'officer_comment',
            'assessor_comment',
            'deficiency',
            'value',
            'licence_activity_id',
            'licence_purpose_id',
        )
        read_only_fields = (
            'field_name',
            'schema_name',
            'component_type',
            'instance_name',
            'officer_comment',
            'assessor_comment',
            'deficiency',
            'value',
            'licence_activity_id',
            'licence_purpose_id',
        )


class BaseApplicationSerializer(serializers.ModelSerializer):
    org_applicant = OrganisationSerializer()
    proxy_applicant = EmailUserAppViewSerializer()
    readonly = serializers.SerializerMethodField(read_only=True)
    licence_type_short_name = serializers.ReadOnlyField()
    documents_url = serializers.SerializerMethodField()
    character_check_status = CustomChoiceField(read_only=True)
    return_check_status = CustomChoiceField(read_only=True)
    application_fee = serializers.DecimalField(
        max_digits=8, decimal_places=2, coerce_to_string=False, read_only=True)
    category_id = serializers.SerializerMethodField(read_only=True)
    category_name = serializers.SerializerMethodField(read_only=True)
    activity_names = serializers.SerializerMethodField(read_only=True)
    activity_purpose_string = serializers.SerializerMethodField(read_only=True)
    purpose_string = serializers.SerializerMethodField(read_only=True)
    amendment_requests = serializers.SerializerMethodField(read_only=True)
    can_current_user_edit = serializers.SerializerMethodField(read_only=True)
    payment_status = serializers.SerializerMethodField(read_only=True)
    can_be_processed = serializers.SerializerMethodField(read_only=True)
    activities = serializers.SerializerMethodField()
    processed = serializers.SerializerMethodField()
    id_check_status = CustomChoiceField(read_only=True)
    processing_status = CustomChoiceField(read_only=True, choices=Application.PROCESSING_STATUS_CHOICES)
    data = ApplicationFormDataRecordSerializer(many=True)
    application_type = CustomChoiceField(read_only=True)

    class Meta:
        model = Application
        fields = (
            'id',
            'data',
            'schema',
            'licence_type_data',
            'licence_type_name',
            'licence_type_short_name',
            'licence_category',
            'customer_status',
            'processing_status',
            'review_status',
            'applicant',
            'org_applicant',
            'proxy_applicant',
            'submitter',
            'previous_application',
            'lodgement_number',
            'lodgement_date',
            'documents',
            'conditions',
            'readonly',
            'can_user_edit',
            'can_user_view',
            'has_amendment',
            'amendment_requests',
            'documents_url',
            'id_check_status',
            'character_check_status',
            'return_check_status',
            'application_fee',
            'category_id',
            'category_name',
            'activity_names',
            'activity_purpose_string',
            'purpose_string',
            'can_current_user_edit',
            'payment_status',
            'assigned_officer',
            'can_be_processed',
            'activities',
            'processed',
            'application_type'
        )
        read_only_fields = ('documents',)

    def get_documents_url(self, obj):
        return '/media/applications/{}/documents/'.format(obj.id)

    def get_readonly(self, obj):
        return False

    def get_payment_status(self, obj):
        return obj.payment_status

    def get_category_id(self, obj):
        return obj.licence_category_id

    def get_category_name(self, obj):
        return obj.licence_category_name

    def get_activity_purpose_string(self, obj):
        activity_names = obj.licence_type_name.split(' - ')[1] if ' - ' in obj.licence_type_name else obj.licence_type_name
        return activity_names

    def get_purpose_string(self, obj):
        return obj.licence_purpose_names

    def get_activity_names(self, obj):
        return obj.licence_activity_names

    def get_activities(self, obj):
        return ApplicationSelectedActivitySerializer(obj.activities, many=True).data

    def get_amendment_requests(self, obj):
        amendment_request_data = []
        # qs = obj.amendment_requests
        # qs = qs.filter(status = 'requested')
        # if qs.exists():
        #     for item in obj.amendment_requests:
        #         print("printing from serializer")
        #         print(item.id)
        #         print(str(item.licence_activity.name))
        #         print(item.licence_activity.id)
        #         amendment_request_data.append({"licence_activity":str(item.licence_activity),"id":item.licence_activity.id})
        return amendment_request_data

    def get_can_be_processed(self, obj):
        return obj.activities.exclude(processing_status__in=[
            ApplicationSelectedActivity.PROCESSING_STATUS_DRAFT,
            ApplicationSelectedActivity.PROCESSING_STATUS_DECLINED,
            ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED,
        ]).exists()

    def get_processed(self, obj):
        """ check if any activities have been processed (i.e. licence issued)"""
        return True if obj.activities.filter(processing_status__in=[
            ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED,
            ApplicationSelectedActivity.PROCESSING_STATUS_DECLINED,
        ]).first() else False

    def get_can_current_user_edit(self, obj):
        result = False
        is_proxy_applicant = False
        is_in_org_applicant = False
        is_app_licence_officer = self.context['request'].user in obj.licence_officers
        is_submitter = obj.submitter == self.context['request'].user
        if obj.proxy_applicant:
            is_proxy_applicant = obj.proxy_applicant == self.context['request'].user
        if obj.org_applicant:
            user_orgs = [
                org.id for org in self.context['request'].user.wildlifecompliance_organisations.all()]
            is_in_org_applicant = obj.org_applicant_id in user_orgs
        if obj.can_user_edit and (
            is_app_licence_officer
            or is_submitter
            or is_proxy_applicant
            or is_in_org_applicant):
                result = True
        return result


class DTInternalApplicationSerializer(BaseApplicationSerializer):
    submitter = EmailUserSerializer()
    applicant = serializers.CharField(read_only=True)
    org_applicant = OrganisationSerializer()
    proxy_applicant = EmailUserSerializer()
    processing_status = CustomChoiceField(read_only=True, choices=Application.PROCESSING_STATUS_CHOICES)
    customer_status = CustomChoiceField(read_only=True)
    can_current_user_edit = serializers.SerializerMethodField(read_only=True)
    payment_status = serializers.SerializerMethodField(read_only=True)
    assigned_officer = serializers.CharField(
        source='assigned_officer.get_full_name')
    can_be_processed = serializers.SerializerMethodField(read_only=True)
    user_in_officers_and_assessors = serializers.SerializerMethodField(read_only=True)
    application_type = CustomChoiceField(read_only=True)

    class Meta:
        model = Application
        fields = (
            'id',
            'customer_status',
            'processing_status',
            'applicant',
            'proxy_applicant',
            'org_applicant',
            'submitter',
            'lodgement_number',
            'lodgement_date',
            'category_id',
            'category_name',
            'activity_names',
            'activity_purpose_string',
            'purpose_string',
            'can_user_view',
            'can_current_user_edit',
            'payment_status',
            'assigned_officer',
            'can_be_processed',
            'user_in_officers_and_assessors',
            'application_type',
            'activities'
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields

    def get_user_in_officers_and_assessors(self, obj):
        if self.context['request'].user and self.context['request'].user in obj.officers_and_assessors:
            return True
        return False


class DTExternalApplicationSerializer(BaseApplicationSerializer):
    submitter = EmailUserSerializer()
    applicant = serializers.CharField(read_only=True)
    org_applicant = ExternalOrganisationSerializer()
    proxy_applicant = EmailUserSerializer()
    processing_status = CustomChoiceField(read_only=True, choices=Application.PROCESSING_STATUS_CHOICES)
    customer_status = CustomChoiceField(read_only=True)
    can_current_user_edit = serializers.SerializerMethodField(read_only=True)
    payment_status = serializers.SerializerMethodField(read_only=True)
    application_type = CustomChoiceField(read_only=True)
    activities = ExternalApplicationSelectedActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = (
            'id',
            'customer_status',
            'processing_status',
            'applicant',
            'org_applicant',
            'proxy_applicant',
            'submitter',
            'lodgement_number',
            'lodgement_date',
            'category_id',
            'category_name',
            'activity_names',
            'activity_purpose_string',
            'purpose_string',
            'can_user_view',
            'can_current_user_edit',
            'payment_status',
            'application_type',
            'activities',
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields


class WildlifeLicenceApplicationSerializer(BaseApplicationSerializer):
    """
    Minimised serializer for WildlifeLicence.current_application
    """
    applicant = serializers.CharField(read_only=True)
    org_applicant = ExternalOrganisationSerializer()
    proxy_applicant = EmailUserSerializer()

    class Meta:
        model = Application
        fields = (
            'id',
            'applicant',
            'org_applicant',
            'proxy_applicant',
            'submitter',
            'category_id',
            'category_name',
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields


class ApplicationSerializer(BaseApplicationSerializer):
    submitter = serializers.CharField(source='submitter.get_full_name')
    processing_status = CustomChoiceField(read_only=True, choices=Application.PROCESSING_STATUS_CHOICES)
    review_status = CustomChoiceField(read_only=True)
    customer_status = CustomChoiceField(read_only=True)
    amendment_requests = serializers.SerializerMethodField(read_only=True)
    can_current_user_edit = serializers.SerializerMethodField(read_only=True)
    payment_status = serializers.SerializerMethodField(read_only=True)
    can_be_processed = serializers.SerializerMethodField(read_only=True)

    def get_readonly(self, obj):
        return not obj.can_user_edit

    def get_amendment_requests(self, obj):
        return ExternalAmendmentRequestSerializer(
            obj.active_amendment_requests.filter(status=AmendmentRequest.AMENDMENT_REQUEST_STATUS_REQUESTED),
            many=True
        ).data


class CreateExternalApplicationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, read_only=True)
    licence_purposes = serializers.ListField(required=False, write_only=True)
    data = ApplicationFormDataRecordSerializer(required=False, many=True)

    class Meta:
        model = Application
        fields = (
            'id',
            'data',
            'schema',
            'licence_type_data',
            'licence_type_name',
            'licence_category',
            'applicant',
            'org_applicant',
            'proxy_applicant',
            'submitter',
            'licence_purposes',
            'application_type',
            'previous_application'
        )


class SaveApplicationSerializer(BaseApplicationSerializer):

    assigned_officer = serializers.CharField(
        source='assigned_officer.get_full_name',
        required=False,
        read_only=True
    )

    class Meta:
        model = Application
        fields = (
            'id',
            'data',
            'comment_data',
            'schema',
            'customer_status',
            'review_status',
            'org_applicant',
            'proxy_applicant',
            'submitter',
            'previous_application',
            'lodgement_date',
            'documents',
            'conditions',
            'readonly',
            'can_user_edit',
            'can_user_view',
            'licence_type_data',
            'licence_type_name',
            'licence_category',
            'application_fee',
            'assigned_officer',
        )
        read_only_fields = ('documents', 'conditions')


class ApplicantSerializer(serializers.ModelSerializer):
    from wildlifecompliance.components.organisations.serializers import OrganisationAddressSerializer
    address = OrganisationAddressSerializer()

    class Meta:
        model = Organisation
        fields = (
            'id',
            'name',
            'abn',
            'address',
            'email',
            'phone_number',
        )


class InternalApplicationSerializer(BaseApplicationSerializer):
    applicant = serializers.CharField(read_only=True)
    org_applicant = OrganisationSerializer()
    proxy_applicant = EmailUserAppViewSerializer()
    processing_status = CustomChoiceField(read_only=True, choices=Application.PROCESSING_STATUS_CHOICES)
    review_status = CustomChoiceField(read_only=True)
    customer_status = CustomChoiceField(read_only=True)
    character_check_status = CustomChoiceField(read_only=True)
    return_check_status = CustomChoiceField(read_only=True)
    submitter = EmailUserAppViewSerializer()
    licences = serializers.SerializerMethodField(read_only=True)
    payment_status = serializers.SerializerMethodField(read_only=True)
    can_be_processed = serializers.SerializerMethodField(read_only=True)
    activities = serializers.SerializerMethodField()
    processed = serializers.SerializerMethodField()
    licence_officers = EmailUserAppViewSerializer(many=True)
    user_in_licence_officers = serializers.SerializerMethodField(read_only=True)
    user_roles = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Application
        fields = (
            'id',
            'data',
            'schema',
            'application_type',
            'customer_status',
            'processing_status',
            'review_status',
            'id_check_status',
            'character_check_status',
            'return_check_status',
            'licence_type_data',
            'applicant',
            'org_applicant',
            'proxy_applicant',
            'submitter',
            'previous_application',
            'lodgement_date',
            'lodgement_number',
            'documents',
            'conditions',
            'readonly',
            'can_user_edit',
            'can_user_view',
            'documents_url',
            'comment_data',
            'licences',
            'permit',
            'payment_status',
            'assigned_officer',
            'can_be_processed',
            'licence_category',
            'activities',
            'processed',
            'licence_officers',
            'user_in_licence_officers',
            'user_roles',
        )
        read_only_fields = ('documents', 'conditions')

    def get_activities(self, obj):
        user = self.context['request'].user
        if user is None:
            return []
        application_activities = ApplicationSelectedActivity.objects.filter(
            application_id=obj.id
        )

        """
        # Uncomment to filter out activities that the internal user cannot assess / process (to hide activity tabs on the UI).
        if not user.has_perm('wildlifecompliance.system_administrator'):
            for activity in application_activities:
                if not user.has_wildlifelicenceactivity_perm([
                    'assessor',
                    'licensing_officer',
                    'issuing_officer',
                ], activity.licence_activity_id):
                    application_activities = application_activities.exclude(licence_activity_id=activity.licence_activity_id)
        """

        return ApplicationSelectedActivitySerializer(application_activities, many=True).data

    def get_readonly(self, obj):
        return True

    def get_licences(self, obj):
        licence_data = []
        active_licences = obj.get_licences_by_status(ApplicationSelectedActivity.ACTIVITY_STATUS_CURRENT)

        for licence in active_licences:
            for activity in licence.current_activities:
                licence_data.append(
                    {
                        "licence_activity": str(
                            activity.licence_activity),
                        "licence_activity_id": activity.licence_activity_id,
                        "start_date": activity.start_date,
                        "expiry_date": activity.expiry_date})
        return licence_data

    def get_processed(self, obj):
        """ check if any activities have been processed """
        return True if obj.activities.filter(processing_status__in=[
            ApplicationSelectedActivity.PROCESSING_STATUS_ACCEPTED,
            ApplicationSelectedActivity.PROCESSING_STATUS_DECLINED
        ]).first() else False

    def get_user_in_licence_officers(self, obj):
        if self.context['request'].user and self.context['request'].user in obj.licence_officers:
            return True
        return False

    def get_user_roles(self, obj):
        try:
            user = self.context['request'].user
        except (KeyError, AttributeError):
            return []

        available_roles = ['assessor', 'licensing_officer', 'issuing_officer', 'return_curator']
        is_administrator = user.has_perm('wildlifecompliance.system_administrator')
        roles = []
        for activity in obj.selected_activities.all():
            for role in available_roles:
                if is_administrator or user.has_wildlifelicenceactivity_perm(role, activity.licence_activity_id):
                    roles.append({'activity_id': activity.licence_activity_id, 'role': role})
        return roles


class ApplicationUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')

    class Meta:
        model = ApplicationUserAction
        fields = '__all__'


class ApplicationLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = ApplicationLogEntry
        fields = '__all__'
        read_only_fields = (
            'customer',
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class ApplicationConditionSerializer(serializers.ModelSerializer):
    due_date = serializers.DateField(
        input_formats=['%d/%m/%Y'],
        required=False,
        allow_null=True)

    class Meta:
        model = ApplicationCondition
        fields = (
            'id',
            'due_date',
            'free_condition',
            'standard_condition',
            'standard',
            'is_default',
            'default_condition',
            'order',
            'application',
            'recurrence',
            'recurrence_schedule',
            'recurrence_pattern',
            'condition',
            'licence_activity',
            'return_type',)
        readonly_fields = ('order', 'condition')


class ApplicationStandardConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStandardCondition
        fields = ('id', 'code', 'text')


class ApplicationProposedIssueSerializer(serializers.ModelSerializer):
    proposed_action = CustomChoiceField(read_only=True)
    decision_action = CustomChoiceField(read_only=True)
    licence_activity = ActivitySerializer()

    class Meta:
        model = ApplicationSelectedActivity
        fields = '__all__'


class ProposedLicenceSerializer(serializers.Serializer):
    expiry_date = serializers.DateField(input_formats=['%d/%m/%Y'], required=False, allow_null=True)
    start_date = serializers.DateField(input_formats=['%d/%m/%Y'], required=False, allow_null=True)
    reason = serializers.CharField()
    cc_email = serializers.CharField(required=False, allow_null=True)
    activity = serializers.ListField(child=serializers.IntegerField())


class ProposedDeclineSerializer(serializers.Serializer):
    reason = serializers.CharField()
    cc_email = serializers.CharField(required=False, allow_null=True)
    activity = serializers.ListField(child=serializers.IntegerField())


class DTAssessmentSerializer(serializers.ModelSerializer):
    assessor_group = ActivityPermissionGroupSerializer(read_only=True)
    status = CustomChoiceField(read_only=True)
    licence_activity = ActivitySerializer(read_only=True)
    submitter = serializers.SerializerMethodField(read_only=True)
    application_lodgement_date = serializers.CharField(
        source='application.lodgement_date')
    applicant = serializers.CharField(source='application.applicant')
    application_category = serializers.CharField(
        source='application.licence_category_name')
    application = serializers.CharField(
        source='application.lodgement_number')
    application_id = serializers.CharField(
        source='application.id')
    application_type = CustomChoiceField(
        source='application.application_type',
        choices=Application.APPLICATION_TYPE_CHOICES,
        read_only=True)

    class Meta:
        model = Assessment
        fields = (
            'id',
            'application',
            'assessor_group',
            'date_last_reminded',
            'status',
            'licence_activity',
            'submitter',
            'application_lodgement_date',
            'applicant',
            'application_category',
            'application_type',
            'application_id'
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data'
        # defined are requested from the serializer. Use datatables_always_serialize to force render
        # of fields that are not listed as 'data' in the datatable columns
        datatables_always_serialize = fields

    def get_submitter(self, obj):
        return EmailUserSerializer(obj.application.submitter).data
