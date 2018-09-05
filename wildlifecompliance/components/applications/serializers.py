from django.conf import settings
from ledger.accounts.models import EmailUser,Address,Document
# from wildlifecompliance.components.applications.utils import amendment_requests
from wildlifecompliance.components.applications.models import (
                                    ApplicationType,
                                    Application,
                                    ApplicationUserAction,
                                    ApplicationLogEntry,
                                    Referral,
                                    ApplicationCondition,
                                    ApplicationStandardCondition,
                                    ApplicationDeclinedDetails,
                                    Assessment,
                                    ApplicationGroupType,
                                    AmendmentRequest
                                )
from wildlifecompliance.components.organisations.models import (
                                Organisation
                            )
from wildlifecompliance.components.licences.models import WildlifeLicenceActivityType
from wildlifecompliance.components.main.serializers import CommunicationLogEntrySerializer 
from wildlifecompliance.components.organisations.serializers import OrganisationSerializer
from wildlifecompliance.components.users.serializers import UserAddressSerializer,DocumentSerializer

from rest_framework import serializers

class ApplicationTypeSerializer(serializers.ModelSerializer):
    activities = serializers.SerializerMethodField()
    class Meta:
        model = ApplicationType
        fields = (
            'id',
            'schema',
            'activities'
        )


    def get_activities(self,obj):
        return obj.activities.names()

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
        fields=('id','name','display_name','licence_class')

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
    payment_status = serializers.SerializerMethodField(read_only=True)
    licence_fee = serializers.DecimalField(max_digits=8, decimal_places=2, coerce_to_string=False)
    class_name = serializers.SerializerMethodField(read_only=True)
    activity_type_names = serializers.SerializerMethodField(read_only=True)
    amendment_requests = serializers.SerializerMethodField(read_only=True)

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
                'customer_status',
                'processing_status',
                'review_status',
                #'hard_copy',
                'applicant',
                'org_applicant',
                'proxy_applicant',
                'submitter',
                'assigned_officer',
                'previous_application',
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
                'payment_status',
                'licence_fee',
                'class_name',
                'activity_type_names'
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

       
class DTApplicationSerializer(BaseApplicationSerializer):
    submitter = EmailUserSerializer()
    applicant = serializers.CharField(read_only=True)
    org_applicant = serializers.CharField(source='org_applicant.organisation.name')
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    assigned_officer = serializers.CharField(source='assigned_officer.get_full_name')

class ApplicationSerializer(BaseApplicationSerializer):
    submitter = serializers.CharField(source='submitter.get_full_name')
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    amendment_requests = serializers.SerializerMethodField(read_only=True)

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
                'assigned_officer',
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
                'application_fee',
                'licence_fee'
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


class ApplicationReferralSerializer(serializers.ModelSerializer):
    referral = serializers.CharField(source='referral.get_full_name')
    processing_status = serializers.CharField(source='get_processing_status_display')
    class Meta:
        model = Referral
        fields = '__all__'

class ApplicationDeclinedDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDeclinedDetails
        fields = '__all__'

class InternalApplicationSerializer(BaseApplicationSerializer):
    applicant = serializers.CharField(read_only=True)
    org_applicant = OrganisationSerializer()
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    id_check_status = serializers.SerializerMethodField(read_only=True)
    character_check_status = serializers.SerializerMethodField(read_only=True)
    #submitter = serializers.CharField(source='submitter.get_full_name')
    submitter = EmailUserAppViewSerializer()
    applicationdeclineddetails = ApplicationDeclinedDetailsSerializer()
    #
    assessor_mode = serializers.SerializerMethodField()
    current_assessor = serializers.SerializerMethodField()
    assessor_data = serializers.SerializerMethodField()
    latest_referrals = ApplicationReferralSerializer(many=True) 
    allowed_assessors = EmailUserSerializer(many=True)

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
                'assigned_officer',
                'assigned_approver',
                'previous_application',
                'lodgement_date',
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
                'latest_referrals',
                'allowed_assessors',
                'proposed_issuance_licence',
                'proposed_decline_status',
                'applicationdeclineddetails',
                'permit'
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

class ReferralApplicationSerializer(InternalApplicationSerializer):
    def get_assessor_mode(self,obj):
        # TODO check if the application has been accepted or declined
        request = self.context['request']
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        referral = Referral.objects.get(application=obj,referral=user)
        return {
            'assessor_mode': True,
            'assessor_can_assess': referral.can_assess_referral(user), 
            'assessor_level': 'referral'
        }

class ReferralSerializer(serializers.ModelSerializer):
    processing_status = serializers.CharField(source='get_processing_status_display')
    class Meta:
        model = Referral
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(ReferralSerializer, self).__init__(*args, **kwargs)
        self.fields['application'] = ReferralApplicationSerializer(context={'request':self.context['request']})

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

class SendReferralSerializer(serializers.Serializer):
    email = serializers.EmailField()

class DTReferralSerializer(serializers.ModelSerializer):
    processing_status = serializers.CharField(source='application.get_processing_status_display')
    referral_status = serializers.CharField(source='get_processing_status_display')
    application_lodgement_date = serializers.CharField(source='application.lodgement_date')
    submitter = serializers.SerializerMethodField()
    referral = EmailUserSerializer()
    class Meta:
        model = Referral
        fields = (
            'id',
            'region',
            'activity',
            'title',
            'applicant',
            'submitter',
            'processing_status',
            'referral_status',
            'lodged_on',
            'application',
            'can_be_processed',
            'referral',
            'application_lodgement_date'
        ) 

    def get_submitter(self,obj):
        return EmailUserSerializer(obj.application.submitter).data

class ApplicationConditionSerializer(serializers.ModelSerializer):
    due_date = serializers.DateField(input_formats=['%d/%m/%Y'],required=False,allow_null=True)
    class Meta:
        model = ApplicationCondition
        fields = ('id','due_date','free_condition','standard_condition','standard','order','application','recurrence','recurrence_schedule','recurrence_pattern','condition','licence_activity_type')
        readonly_fields = ('order','condition')

class ApplicationStandardConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStandardCondition
        fields = ('id','code','text')

class ProposedLicenceSerializer(serializers.Serializer):
    expiry_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    start_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    details = serializers.CharField()
    cc_email = serializers.CharField(required=False,allow_null=True)

class PropedDeclineSerializer(serializers.Serializer):
    reason = serializers.CharField()
    cc_email = serializers.CharField(required=False)
    activity_type=serializers.ListField(child=serializers.IntegerField())
