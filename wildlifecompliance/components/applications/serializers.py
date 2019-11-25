from django.conf import settings
from ledger.accounts.models import EmailUser,Address,Document
# from wildlifecompliance.components.applications.utils import amendment_requests
from wildlifecompliance.components.applications.models import (
                                    Application,
                                    ApplicationUserAction,
                                    ApplicationLogEntry,
                                    ApplicationCondition,
                                    ApplicationStandardCondition,
                                    ApplicationDeclinedDetails,
                                    Assessment,
                                    ApplicationGroupType,
                                    AmendmentRequest,
                                    ApplicationDecisionPropose
                                )
from wildlifecompliance.components.organisations.models import (
                                Organisation
                            )
from wildlifecompliance.components.licences.models import WildlifeLicenceActivityType
from wildlifecompliance.components.main.serializers import CommunicationLogEntrySerializer
from wildlifecompliance.components.organisations.serializers import OrganisationSerializer
from wildlifecompliance.components.users.serializers import UserAddressSerializer,DocumentSerializer
from wildlifecompliance import helpers, settings

from rest_framework import serializers


class EmailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = ('id','email','first_name','last_name','title','organisation')

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

class ApplicationGroupTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ApplicationGroupType
        fields=('id','name','display_name','licence_class', 'licence_activity_type')

class AssessmentSerializer(serializers.ModelSerializer):
    assessor_group = ApplicationGroupTypeSerializer(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model=Assessment
        fields=('id','application','assessor_group','date_last_reminded','status','licence_activity_type')

    def get_status(self,obj):
        return obj.get_status_display()


class SaveAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Assessment
        fields=('assessor_group','application','text','licence_activity_type')

class ActivityTypeserializer(serializers.ModelSerializer):
    class Meta:
        model= WildlifeLicenceActivityType
        fields=('id','name','short_name')





class AmendmentRequestSerializer(serializers.ModelSerializer):
    reason = serializers.SerializerMethodField()

    class Meta:
        model = AmendmentRequest
        fields = '__all__'

    def get_reason (self,obj):
        return obj.get_reason_display()

class ExternalAmendmentRequestSerializer(serializers.ModelSerializer):

    licence_activity_type=ActivityTypeserializer(read_only=True)

    class Meta:
        model = AmendmentRequest
        fields = '__all__'



class BaseApplicationSerializer(serializers.ModelSerializer):
    readonly = serializers.SerializerMethodField(read_only=True)
    licence_type_short_name = serializers.ReadOnlyField()
    documents_url = serializers.SerializerMethodField()
    character_check_status = serializers.SerializerMethodField(read_only=True)
    application_fee = serializers.DecimalField(max_digits=8, decimal_places=2, coerce_to_string=False)
    licence_fee = serializers.DecimalField(max_digits=8, decimal_places=2, coerce_to_string=False)
    class_name = serializers.SerializerMethodField(read_only=True)
    activity_type_names = serializers.SerializerMethodField(read_only=True)
    amendment_requests = serializers.SerializerMethodField(read_only=True)
    can_current_user_edit = serializers.SerializerMethodField(read_only=True)

    if settings.WC_VERSION != "1.0":
        payment_status = serializers.SerializerMethodField(read_only=True)
        assigned_officer = serializers.CharField(source='assigned_officer.get_full_name')
        can_be_processed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Application
        fields = (
            'id',
            'activity',
            'title',
            'region',
            'data',
            'schema',
            'licence_type_data',
            'licence_type_name',
            'licence_type_short_name',
            'licence_category',
            'customer_status',
            'processing_status',
            'review_status',
            #'hard_copy',
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
            'application_fee',
            'licence_fee',
            'class_name',
            'activity_type_names',
            'can_current_user_edit'
        )
        if settings.WC_VERSION != "1.0":
            fields += (
                'payment_status',
                'assigned_officer',
                'can_be_processed'
            )
        read_only_fields=('documents',)

    def get_documents_url(self,obj):
        return '/media/applications/{}/documents/'.format(obj.id)

    def get_readonly(self,obj):
        return False

    def get_processing_status(self,obj):
        return obj.get_processing_status_display()

    def get_id_check_status(self,obj):
        return obj.get_id_check_status_display()

    def get_character_check_status(self,obj):
        return obj.get_character_check_status_display()

    def get_review_status(self,obj):
        return obj.get_review_status_display()

    def get_customer_status(self,obj):
        return obj.get_customer_status_display()

    def get_payment_status(self,obj):
        return obj.payment_status

    def get_class_name(self, obj):
        for item in obj.licence_type_data:
            if item == "name":
                return obj.licence_type_data["name"]
        return obj.licence_type_data["id"]

    def get_activity_type_names(self, obj):
        activity_type=[]
        for item in obj.licence_type_data["activity_type"]:
           if "short_name" in item:
            activity_type.append(item["short_name"])
           else:
            activity_type.append(item["name"])

        return activity_type

    def get_amendment_requests(self, obj):
        amendment_request_data=[]
        # qs = obj.amendment_requests
        # qs = qs.filter(status = 'requested')
        # if qs.exists():
        #     for item in obj.amendment_requests:
        #         print("printing from serializer")
        #         print(item.id)
        #         print(str(item.licence_activity_type.name))
        #         print(item.licence_activity_type.id)
        #         amendment_request_data.append({"licence_activity_type":str(item.licence_activity_type),"id":item.licence_activity_type.id})
        return amendment_request_data

    def get_can_be_processed(self, obj):
        return obj.processing_status == 'under_review'

    def get_can_current_user_edit(self, obj):
        result = False
        is_proxy_applicant = False
        is_in_org_applicant = False
        is_officer = helpers.is_officer(self.context['request'])
        is_submitter = obj.submitter == self.context['request'].user
        if obj.proxy_applicant:
            is_proxy_applicant = obj.proxy_applicant == self.context['request'].user
        if obj.org_applicant:
            user_orgs = [org.id for org in self.context['request'].user.wildlifecompliance_organisations.all()]
            is_in_org_applicant = obj.org_applicant_id in user_orgs
        if obj.can_user_edit and (is_officer or is_submitter or is_proxy_applicant or is_in_org_applicant):
            result = True
        return result


class DTInternalApplicationSerializer(BaseApplicationSerializer):
    submitter = EmailUserSerializer()
    applicant = serializers.CharField(read_only=True)
    proxy_applicant = EmailUserSerializer()
    processing_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    can_current_user_edit = serializers.SerializerMethodField(read_only=True)

    if settings.WC_VERSION != "1.0":
        payment_status = serializers.SerializerMethodField(read_only=True)
        assigned_officer = serializers.CharField(source='assigned_officer.get_full_name')
        can_be_processed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Application
        fields = (
            'id',
            'customer_status',
            'processing_status',
            'applicant',
            'proxy_applicant',
            'submitter',
            'lodgement_number',
            'lodgement_date',
            'class_name',
            'activity_type_names',
            'can_user_view',
            'can_current_user_edit'
        )
        if settings.WC_VERSION != "1.0":
            fields += (
                'payment_status',
                'assigned_officer',
                'can_be_processed'
            )


class DTExternalApplicationSerializer(BaseApplicationSerializer):
    submitter = EmailUserSerializer()
    applicant = serializers.CharField(read_only=True)
    proxy_applicant = EmailUserSerializer()
    processing_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    can_current_user_edit = serializers.SerializerMethodField(read_only=True)

    if settings.WC_VERSION != "1.0":
        payment_status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Application
        fields = (
            'id',
            'customer_status',
            'processing_status',
            'applicant',
            'proxy_applicant',
            'submitter',
            'lodgement_number',
            'lodgement_date',
            'class_name',
            'activity_type_names',
            'can_user_view',
            'can_current_user_edit'
        )
        if settings.WC_VERSION != "1.0":
            fields += (
                'payment_status',
            )

class ApplicationSerializer(BaseApplicationSerializer):
    submitter = serializers.CharField(source='submitter.get_full_name')
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    amendment_requests = serializers.SerializerMethodField(read_only=True)
    can_current_user_edit = serializers.SerializerMethodField(read_only=True)

    if settings.WC_VERSION != "1.0":
        payment_status = serializers.SerializerMethodField(read_only=True)
        assigned_officer = serializers.CharField(source='assigned_officer.get_full_name')
        can_be_processed = serializers.SerializerMethodField(read_only=True)

    def get_readonly(self,obj):
        return obj.can_user_view

    def get_amendment_requests(self, obj):
        amendment_request_data=[]
        qs = obj.amendment_requests
        qs = qs.filter(status = 'requested')
        if qs.exists():
            for item in obj.amendment_requests:
                print("printing from serializer")
                print(item.id)
                print(str(item.licence_activity_type.name))
                print(item.licence_activity_type.id)
                # amendment_request_data.append({"licence_activity_type":str(item.licence_activity_type),"id":item.licence_activity_type.id})
                amendment_request_data.append(item.licence_activity_type.id)
        return amendment_request_data




class SaveApplicationSerializer(BaseApplicationSerializer):
    assessor_data = serializers.JSONField(required=False)
    # licence_activity_type=ActivityTypeserializer(many=True,read_only =True)

    if settings.WC_VERSION != "1.0":
        assigned_officer = serializers.CharField(source='assigned_officer.get_full_name')

    class Meta:
        model = Application
        fields = (
                'id',
                'activity',
                'title',
                'region',
                'data',
                'assessor_data',
                'comment_data',
                'schema',
                'customer_status',
                'processing_status',
                'review_status',
                #'hard_copy',
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
                # 'licence_category',
                'licence_type_data',
                'licence_type_name',
                'licence_category',
                'application_fee',
                'licence_fee'
                )
        if settings.WC_VERSION != "1.0":
            fields += (
                'assigned_officer',
            )
        read_only_fields=('documents','conditions')

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


class ApplicationDeclinedDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDeclinedDetails
        fields = '__all__'

class InternalApplicationSerializer(BaseApplicationSerializer):
    applicant = serializers.CharField(read_only=True)
    org_applicant = OrganisationSerializer()
    proxy_applicant = EmailUserAppViewSerializer()
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    id_check_status = serializers.SerializerMethodField(read_only=True)
    character_check_status = serializers.SerializerMethodField(read_only=True)
    submitter = EmailUserAppViewSerializer()
    applicationdeclineddetails = ApplicationDeclinedDetailsSerializer()
    assessor_mode = serializers.SerializerMethodField()
    current_assessor = serializers.SerializerMethodField()
    assessor_data = serializers.SerializerMethodField()
    allowed_assessors = EmailUserSerializer(many=True)
    licences = serializers.SerializerMethodField(read_only=True)

    if settings.WC_VERSION != "1.0":
        payment_status = serializers.SerializerMethodField(read_only=True)
        assigned_officer = serializers.CharField(source='assigned_officer.get_full_name')
        can_be_processed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Application
        fields = (
                'id',
                'activity',
                'title',
                'region',
                'data',
                'schema',
                'customer_status',
                'processing_status',
                'review_status',
                'id_check_status',
                'character_check_status',
                'licence_type_data',
                #'hard_copy',
                'applicant',
                'org_applicant',
                'proxy_applicant',
                'submitter',
                'assigned_approver',
                'previous_application',
                'lodgement_date',
                'lodgement_number',
                'documents',
                'conditions',
                'readonly',
                'can_user_edit',
                'can_user_view',
                'documents_url',
                'assessor_mode',
                'current_assessor',
                'assessor_data',
                'comment_data',
                'licences',
                'allowed_assessors',
                'proposed_issuance_licence',
                'proposed_decline_status',
                'applicationdeclineddetails',
                'permit'
                )
        if settings.WC_VERSION != "1.0":
            fields += (
                'payment_status',
                'assigned_officer',
                'can_be_processed'
            )
        read_only_fields=('documents','conditions')

    def get_assessor_mode(self,obj):
        # TODO check if the application has been accepted or declined
        request = self.context['request']
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        return {
            'assessor_mode': True,
            # 'has_assessor_mode': obj.has_assessor_mode(user),
            'has_assessor_mode': True,
            # 'assessor_can_assess': obj.can_assess(user),
            'assessor_level': 'assessor'
        }

    def get_id_check_status(self,obj):
        return obj.get_id_check_status_display()

    def get_character_check_status(self,obj):
        return obj.get_character_check_status_display()

    def get_readonly(self,obj):
        return True

    def get_current_assessor(self,obj):
        return {
            'id': self.context['request'].user.id,
            'name': self.context['request'].user.get_full_name(),
            'email': self.context['request'].user.email
        }

    def get_assessor_data(self,obj):
        return obj.assessor_data

    def get_licences(self, obj):
        licence_data=[]
        qs = obj.licences

        if qs.exists():
            qs = qs.filter(status = 'current')
            for item in obj.licences:
                # print(item)
                # print(item.status)
                print(item.licence_activity_type_id)
                # print(item.parent_licence)

                # amendment_request_data.append({"licence_activity_type":str(item.licence_activity_type),"id":item.licence_activity_type.id})
                licence_data.append({"licence_activity_type":str(item.licence_activity_type),"licence_activity_type_id":item.licence_activity_type_id,"start_date":item.start_date,"expiry_date":item.expiry_date})
        return licence_data


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

    def get_documents(self,obj):
        return [[d.name,d._file.url] for d in obj.documents.all()]


class ApplicationConditionSerializer(serializers.ModelSerializer):
    due_date = serializers.DateField(input_formats=['%d/%m/%Y'],required=False,allow_null=True)
    class Meta:
        model = ApplicationCondition
        fields = ('id','due_date','free_condition','standard_condition','standard','is_default','default_condition','order','application','recurrence','recurrence_schedule','recurrence_pattern','condition','licence_activity_type')
        readonly_fields = ('order','condition')

class ApplicationStandardConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStandardCondition
        fields = ('id','code','text')

class ApplicationProposedIssueSerializer(serializers.ModelSerializer):
    proposed_action = serializers.SerializerMethodField(read_only=True)
    decision_action = serializers.SerializerMethodField(read_only=True)
    licence_activity_type = ActivityTypeserializer()

    class Meta:
        model = ApplicationDecisionPropose
        fields = '__all__'

    def get_proposed_action(self,obj):
        return obj.get_proposed_action_display()

    def get_decision_action(self,obj):
        return obj.get_decision_action_display()




class ProposedLicenceSerializer(serializers.Serializer):
    expiry_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    start_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    reason = serializers.CharField()
    cc_email = serializers.CharField(required=False,allow_null=True)
    activity_type=serializers.ListField(child=serializers.IntegerField())


class ProposedDeclineSerializer(serializers.Serializer):
    reason = serializers.CharField()
    cc_email = serializers.CharField(required=False,allow_null=True)
    activity_type=serializers.ListField(child=serializers.IntegerField())


class DTAssessmentSerializer(serializers.ModelSerializer):
    assessor_group = ApplicationGroupTypeSerializer(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    licence_activity_type = ActivityTypeserializer(read_only=True)
    submitter = serializers.SerializerMethodField(read_only=True)
    application_lodgement_date = serializers.CharField(source='application.lodgement_date')
    applicant = serializers.CharField(source='application.applicant')
    application_category = serializers.CharField(source='application.licence_type_name')

    class Meta:
        model = Assessment
        fields = (
            'id',
            'application',
            'assessor_group',
            'date_last_reminded',
            'status',
            'licence_activity_type',
            'submitter',
            'application_lodgement_date',
            'applicant',
            'application_category'
        )

    def get_submitter(self, obj):
        return EmailUserSerializer(obj.application.submitter).data

    def get_status(self,obj):
        return obj.get_status_display()
