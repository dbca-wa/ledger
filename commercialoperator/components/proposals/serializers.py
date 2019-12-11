from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from commercialoperator.components.proposals.models import (
                                    ProposalType,
                                    Proposal,
                                    ProposalUserAction,
                                    ProposalLogEntry,
                                    Referral,
                                    ProposalRequirement,
                                    ProposalStandardRequirement,
                                    ProposalDeclinedDetails,
                                    AmendmentRequest,
                                    AmendmentReason,
                                    ProposalApplicantDetails,
                                    ProposalActivitiesLand,
                                    ProposalActivitiesMarine,
                                    ProposalPark,
                                    ProposalParkActivity,
                                    Vehicle,
                                    Vessel,
                                    ProposalTrail,
                                    QAOfficerReferral,
                                    ProposalParkAccess,
                                    ProposalTrailSection,
                                    ProposalTrailSectionActivity,
                                    ProposalParkZoneActivity,
                                    ProposalParkZone,
                                    ProposalOtherDetails,
                                    ProposalAccreditation,
                                    ChecklistQuestion,
                                    ProposalAssessmentAnswer,
                                    ProposalAssessment,
                                    RequirementDocument,
                                )
from commercialoperator.components.organisations.models import (
                                Organisation
                            )
from commercialoperator.components.main.serializers import CommunicationLogEntrySerializer, ParkSerializer, ActivitySerializer, AccessTypeSerializer, TrailSerializer
from commercialoperator.components.organisations.serializers import OrganisationSerializer
from commercialoperator.components.users.serializers import UserAddressSerializer, DocumentSerializer
from rest_framework import serializers
from django.db.models import Q
from reversion.models import Version

class ProposalTypeSerializer(serializers.ModelSerializer):
    activities = serializers.SerializerMethodField()
    class Meta:
        model = ProposalType
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

class ProposalApplicantDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalApplicantDetails
        fields = ('id','first_name')

class ProposalActivitiesLandSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalActivitiesLand
        fields = ('id','activities_land')

class ProposalActivitiesMarineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalActivitiesMarine
        fields = ('id','activities_marine')

#class ParkEntrySerializer(serializers.ModelSerializer):
#    class Meta:
#        model = ParkEntry
#        fields = '__all__'

class ProposalParkActivitySerializer(serializers.ModelSerializer):
    activity=ActivitySerializer()
    #park_entry=ParkEntrySerializer()
    class Meta:
        model = ProposalParkActivity
        fields = '__all__'

class ProposalParkAccessSerializer(serializers.ModelSerializer):
    access_type=AccessTypeSerializer()
    class Meta:
        model = ProposalParkAccess
        fields = '__all__'

class ProposalParkZoneActivitySerializer(serializers.ModelSerializer):
    #activities=ProposalTrailSectionActivitySerializer(many=True)
    class Meta:
        model = ProposalParkZoneActivity
        fields = ('activity',)
        #fields = '__all__'

class ProposalParkZoneSerializer(serializers.ModelSerializer):
    # trail=TrailSerializer()
    # sections=ProposalTrailSectionSerializer()
    park_activities=ProposalParkZoneActivitySerializer(many=True)
    class Meta:
        model = ProposalParkZone
        fields = ('zone','access_point','park_activities')
        #fields = '__all__'

class ProposalParkSerializer(serializers.ModelSerializer):
    park=ParkSerializer()
    land_activities=ProposalParkActivitySerializer(many=True)
    #marine_activities=ProposalParkActivitySerializer(many=True)
    zones=ProposalParkZoneSerializer(many=True)
    access_types=ProposalParkAccessSerializer(many=True)
    class Meta:
        model = ProposalPark
        fields = '__all__'

class SaveProposalParkSerializer(serializers.ModelSerializer):
    #park=ParkSerializer()
    class Meta:
        model = ProposalPark
        fields = '__all__'

class ProposalTrailSectionActivitySerializer(serializers.ModelSerializer):
    #activities=ProposalTrailSectionActivitySerializer(many=True)
    class Meta:
        model = ProposalTrailSectionActivity
        fields = ('activity',)
        #fields = '__all__'

class ProposalTrailSectionSerializer(serializers.ModelSerializer):
    # trail=TrailSerializer()
    # sections=ProposalTrailSectionSerializer()
    trail_activities=ProposalTrailSectionActivitySerializer(many=True)
    class Meta:
        model = ProposalTrailSection
        fields = ('section','trail_activities')
        #fields = '__all__'

class ProposalTrailSerializer(serializers.ModelSerializer):
    trail=TrailSerializer()
    sections=ProposalTrailSectionSerializer(many=True)
    #land_activities=ProposalParkActivitySerializer(many=True)
    class Meta:
        model = ProposalTrail
        fields = '__all__'

class SaveProposalTrailSerializer(serializers.ModelSerializer):
    #park=ParkSerializer()
    class Meta:
        model = ProposalTrail
        fields = '__all__'

class QAOfficerReferralSerializer(serializers.ModelSerializer):
    processing_status = serializers.SerializerMethodField(read_only=True)
    sent_by = serializers.SerializerMethodField(read_only=True)
    qaofficer = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = QAOfficerReferral
        fields = '__all__'

    def get_processing_status(self,obj):
        return obj.get_processing_status_display()

    def get_sent_by(self,obj):
        return obj.sent_by.get_full_name() if obj.sent_by else ''

    def get_qaofficer(self,obj):
        return obj.qaofficer.get_full_name() if obj.qaofficer else ''

class ProposalAccreditationSerializer(serializers.ModelSerializer):
    accreditation_type_value= serializers.SerializerMethodField()
    accreditation_expiry = serializers.DateField(format="%d/%m/%Y",input_formats=['%d/%m/%Y'],required=False,allow_null=True)

    class Meta:
        model = ProposalAccreditation
        #fields = '__all__'
        fields=('id',
                'accreditation_type',
                'accreditation_expiry',
                'comments',
                'proposal_other_details',
                'accreditation_type_value'
                )

    def get_accreditation_type_value(self,obj):
        return obj.get_accreditation_type_display()


class ProposalOtherDetailsSerializer(serializers.ModelSerializer):
    #park=ParkSerializer()
    #accreditation_type= serializers.SerializerMethodField()
    #accreditation_expiry = serializers.DateField(format="%d/%m/%Y",input_formats=['%d/%m/%Y'],required=False,allow_null=True)
    nominated_start_date = serializers.DateField(format="%d/%m/%Y",input_formats=['%d/%m/%Y'],required=False,allow_null=True)
    insurance_expiry = serializers.DateField(format="%d/%m/%Y",input_formats=['%d/%m/%Y'],required=False,allow_null=True)
    accreditations = ProposalAccreditationSerializer(many=True, read_only=True)
    preferred_licence_period = serializers.CharField(allow_blank=True, allow_null=True)
    proposed_end_date = serializers.DateField(format="%d/%m/%Y",read_only=True)

    class Meta:
        model = ProposalOtherDetails
        #fields = '__all__'
        fields=(
                #'accreditation_type',
                #'accreditation_expiry',
                'id',
                'accreditations',
                'preferred_licence_period',
                'nominated_start_date',
                'insurance_expiry',
                'other_comments',
                'credit_fees',
                'credit_docket_books',
                'docket_books_number',
                'mooring',
                'proposed_end_date',
                )
    # def get_accreditation_type(self,obj):
    #     return obj.get_accreditation_type_display()

class SaveProposalOtherDetailsSerializer(serializers.ModelSerializer):
    #park=ParkSerializer()
    class Meta:
        model = ProposalOtherDetails
        #fields = '__all__'
        fields=(
                # 'accreditation_type',
                # 'accreditation_expiry',
                'preferred_licence_period',
                'nominated_start_date',
                'insurance_expiry',
                'other_comments',
                'credit_fees',
                'credit_docket_books',
                'proposal',
                )
class ChecklistQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChecklistQuestion
        #fields = '__all__'
        fields=('id',
                'text',
                'answer_type',
                )
class ProposalAssessmentAnswerSerializer(serializers.ModelSerializer):
    question=ChecklistQuestionSerializer(read_only=True)
    class Meta:
        model = ProposalAssessmentAnswer
        fields = ('id',
                'question',
                'answer',
                'text_answer',
                )

class ProposalAssessmentSerializer(serializers.ModelSerializer):
    checklist=ProposalAssessmentAnswerSerializer(many=True, read_only=True)

    class Meta:
        model = ProposalAssessment
        fields = ('id',
                'completed',
                'submitter',
                'referral_assessment',
                'referral_group',
                'referral_group_name',
                'checklist'
                )


class BaseProposalSerializer(serializers.ModelSerializer):
    #org_applicant = OrganisationSerializer()
    readonly = serializers.SerializerMethodField(read_only=True)
    documents_url = serializers.SerializerMethodField()
    proposal_type = serializers.SerializerMethodField()
    allowed_assessors = EmailUserSerializer(many=True)
    #qaofficer_referral = QAOfficerReferralSerializer(required=False)
    qaofficer_referrals = QAOfficerReferralSerializer(many=True)

    #applicant_details = ProposalApplicantDetailsSerializer(required=False)
    activities_land = ProposalActivitiesLandSerializer(required=False)
    activities_marine = ProposalActivitiesMarineSerializer(required=False)
    land_parks=ProposalParkSerializer(many=True)
    marine_parks=ProposalParkSerializer(many=True)
    trails=ProposalTrailSerializer(many=True)
    other_details=ProposalOtherDetailsSerializer()

    get_history = serializers.ReadOnlyField()
    is_qa_officer = serializers.SerializerMethodField()
    fee_invoice_url = serializers.SerializerMethodField()
    land_access = serializers.SerializerMethodField()
    land_activities = serializers.SerializerMethodField()
    trail_activities = serializers.SerializerMethodField()
    trail_section_activities = serializers.SerializerMethodField()

#    def __init__(self, *args, **kwargs):
#        user = kwargs['context']['request'].user
#
#        super(BaseProposalSerializer, self).__init__(*args, **kwargs)
#        self.fields['parent'].queryset = self.get_request(user)

    class Meta:
        model = Proposal
        fields = (
                'id',
                'application_type',
                'activity',
                'approval_level',
                'title',
                'region',
                'district',
                'tenure',
                #'assessor_data',
                'data',
                'schema',
                'customer_status',
                'processing_status',
                'review_status',
                #'hard_copy',
                'applicant_type',
                'applicant',
                'org_applicant',
                'proxy_applicant',
                'submitter',
                'assigned_officer',
                'previous_application',
                'get_history',
                'lodgement_date',
                'modified_date',
                'documents',
                'requirements',
                'readonly',
                'can_user_edit',
                'can_user_view',
                'documents_url',
                'reference',
                'lodgement_number',
                'lodgement_sequence',
                'can_officer_process',
                'allowed_assessors',
                'proposal_type',
                'is_qa_officer',
                'qaofficer_referrals',
                'pending_amendment_request',
                'is_amendment_proposal',

                # tab field models
                'applicant_details',
                'other_details',
                'activities_land',
                'activities_marine',
                'land_access',
                'land_activities',
                'trail_activities',
                'trail_section_activities',
                'land_parks',
                'marine_parks',
                'trails',
                'training_completed',
                'fee_invoice_url',
                'fee_paid',

                )
        read_only_fields=('documents',)

    def get_documents_url(self,obj):
        return '/media/{}/proposals/{}/documents/'.format(settings.MEDIA_APP_DIR, obj.id)

    def get_readonly(self,obj):
        return False

    def get_processing_status(self,obj):
        return obj.get_processing_status_display()

    def get_review_status(self,obj):
        return obj.get_review_status_display()

    def get_customer_status(self,obj):
        return obj.get_customer_status_display()

    def get_proposal_type(self,obj):
        return obj.get_proposal_type_display()

    def get_is_qa_officer(self,obj):
        request = self.context['request']
        return request.user.email in obj.qa_officers()

    def get_fee_invoice_url(self,obj):
        return '/cols/payments/invoice-pdf/{}'.format(obj.fee_invoice_reference) if obj.fee_paid else None

    def get_land_access(self,obj):
        return obj.land_parks.filter(access_types__isnull=False).values_list('access_types__access_type_id', flat=True).distinct()

    def get_land_activities(self,obj):
        return obj.land_parks.filter(activities__isnull=False).values_list('activities__activity_id', flat=True).distinct()

    def get_trail_activities(self,obj):
        return ProposalTrailSectionActivity.objects.filter(trail_section__proposal_trail__proposal=obj.id).values_list('activity',flat=True).distinct()

    def get_trail_section_activities(self,obj):
        return obj.trails.all().values_list('trail_id', flat=True)

#Not used anymore
class DTProposalSerializer(BaseProposalSerializer):
    submitter = EmailUserSerializer()
    applicant = serializers.CharField(source='applicant.organisation.name')
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    assigned_officer = serializers.CharField(source='assigned_officer.get_full_name', allow_null=True)

    application_type = serializers.CharField(source='application_type.name', read_only=True)
    region = serializers.CharField(source='region.name', read_only=True)
    district = serializers.CharField(source='district.name', read_only=True)
    #tenure = serializers.CharField(source='tenure.name', read_only=True)


class ListProposalSerializer(BaseProposalSerializer):
    submitter = EmailUserSerializer()
    applicant = serializers.CharField(read_only=True)
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    #assigned_officer = serializers.CharField(source='assigned_officer.get_full_name')
    assigned_officer = serializers.SerializerMethodField(read_only=True)

    application_type = serializers.CharField(source='application_type.name', read_only=True)
    #region = serializers.CharField(source='region.name', read_only=True)
    #district = serializers.CharField(source='district.name', read_only=True)
    region = serializers.SerializerMethodField(read_only=True)
    district = serializers.SerializerMethodField(read_only=True)

    #tenure = serializers.CharField(source='tenure.name', read_only=True)
    assessor_process = serializers.SerializerMethodField(read_only=True)
    qaofficer_referrals = QAOfficerReferralSerializer(many=True)
    fee_invoice_url = serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = (
                'id',
                'application_type',
                'activity',
                'approval_level',
                'title',
                'region',
                'district',
                'tenure',
                'customer_status',
                'processing_status',
                'review_status',
                'applicant',
                'proxy_applicant',
                'submitter',
                'assigned_officer',
                'previous_application',
                'get_history',
                'lodgement_date',
                'modified_date',
                'readonly',
                'can_user_edit',
                'can_user_view',
                'reference',
                'lodgement_number',
                'lodgement_sequence',
                'can_officer_process',
                'assessor_process',
                'allowed_assessors',
                'proposal_type',
                'qaofficer_referrals',
                'is_qa_officer',
                'fee_invoice_url',
                'fee_invoice_reference',
                'fee_paid',
                )
        # the serverSide functionality of datatables is such that only columns that have field 'data' defined are requested from the serializer. We
        # also require the following additional fields for some of the mRender functions
        datatables_always_serialize = (
                'id',
                'activity',
                'title',
                'region',
                'customer_status',
                'processing_status',
                'applicant',
                'submitter',
                'assigned_officer',
                'lodgement_date',
                'can_user_edit',
                'can_user_view',
                'reference',
                'lodgement_number',
                'can_officer_process',
                'assessor_process',
                'allowed_assessors',
                'fee_invoice_url',
                'fee_invoice_reference',
                'fee_paid',
                )

    def get_assigned_officer(self,obj):
        if obj.assigned_officer:
            return obj.assigned_officer.get_full_name()
        return None

    def get_region(self,obj):
        if obj.region:
            return obj.region.name
        return None

    def get_district(self,obj):
        if obj.district:
            return obj.district.name
        return None

    def get_assessor_process(self,obj):
        # Check if currently logged in user has access to process the proposal
        request = self.context['request']
        user = request.user
        if obj.can_officer_process:
            '''if (obj.assigned_officer and obj.assigned_officer == user) or (user in obj.allowed_assessors):
                return True'''
            if obj.assigned_officer:
                if obj.assigned_officer == user:
                    return True
            elif user in obj.allowed_assessors:
                return True
        return False

    def get_is_qa_officer(self,obj):
        request = self.context['request']
        return request.user.email in obj.qa_officers()

    def get_fee_invoice_url(self,obj):
        return '/cols/payments/invoice-pdf/{}'.format(obj.fee_invoice_reference) if obj.fee_paid else None

class ProposalSerializer(BaseProposalSerializer):
    submitter = serializers.CharField(source='submitter.get_full_name')
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)

    application_type = serializers.CharField(source='application_type.name', read_only=True)
    region = serializers.CharField(source='region.name', read_only=True)
    district = serializers.CharField(source='district.name', read_only=True)

    #tenure = serializers.CharField(source='tenure.name', read_only=True)

    def get_readonly(self,obj):
        return obj.can_user_view

#class ProposalApplicantDetailsSerializer(serializers.ModelSerializer):
#
#    class Meta:
#        model = ProposalApplicantDetails
#        fields = (
#                'id',
#                'first_name',
#                )

class SaveProposalSerializer(BaseProposalSerializer):
    assessor_data = serializers.JSONField(required=False)
    #applicant_details = ProposalApplicantDetailsSerializer(required=False)
    #other_details= SaveProposalOtherDetailsSerializer()

    class Meta:
        model = Proposal
        fields = (
                'id',
                'application_type',
                'activity',
                'approval_level',
                'title',
                'region',
                'district',
                'tenure',
                'data',
                'assessor_data',
                'comment_data',
                'schema',
                'customer_status',
                'processing_status',
                'review_status',
                #'hard_copy',
                'applicant_type',
                'applicant',
                'org_applicant',
                'proxy_applicant',
                'submitter',
                'assigned_officer',
                'previous_application',
                'lodgement_date',
                'documents',
                'requirements',
                'readonly',
                'can_user_edit',
                'can_user_view',
                'reference',
                'lodgement_number',
                'lodgement_sequence',
                'can_officer_process',
                'applicant_details',
                #'activities_land',
                #'activities_marine',
                #'other_details',
                )
        read_only_fields=('documents','requirements',)



class ApplicantSerializer(serializers.ModelSerializer):
    from commercialoperator.components.organisations.serializers import OrganisationAddressSerializer
    address = OrganisationAddressSerializer(read_only=True)
    #address = OrganisationAddressSerializer()
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


class ProposalReferralSerializer(serializers.ModelSerializer):
    #referral = serializers.CharField(source='referral.get_full_name')
    referral = serializers.CharField(source='referral_group.name')
    processing_status = serializers.CharField(source='get_processing_status_display')
    class Meta:
        model = Referral
        fields = '__all__'

class ProposalDeclinedDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalDeclinedDetails
        fields = '__all__'

class ProposalParkSerializer(BaseProposalSerializer):
    applicant = ApplicantSerializer()
    processing_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    submitter = serializers.CharField(source='submitter.get_full_name')
    application_type = serializers.CharField(source='application_type.name', read_only=True)
    licence_number = serializers.SerializerMethodField(read_only=True)
    licence_number_id = serializers.SerializerMethodField(read_only=True)
    land_parks=ProposalParkSerializer(source='land_parks_exclude_free', many=True)

    class Meta:
        model = Proposal
        fields = (
                'id',
                'licence_number',
                'licence_number_id',
                'application_type',
                'approval_level',
                'title',
                'customer_status',
                'processing_status',
                'applicant',
                'proxy_applicant',
                'submitter',
                'lodgement_number',
                #'activities_land',
                #'activities_marine',
                #'land_parks_exclude_free',
                'land_parks',
                #'marine_parks',
                #'trails',
                )
        #read_only_fields=('documents','requirements')
        #read_only_fields = '__all__'

    def get_licence_number(self,obj):
        return obj.approval.lodgement_number

    def get_licence_number_id(self,obj):
        return obj.approval.id

    def get_land_parks(self,obj):
        """ exlude parks with free admission """
        return obj.land_parks_exclude_free

class InternalProposalSerializer(BaseProposalSerializer):
    #applicant = ApplicantSerializer()
    applicant = serializers.CharField(read_only=True)
    org_applicant = OrganisationSerializer()
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    #submitter = serializers.CharField(source='submitter.get_full_name')
    submitter = EmailUserAppViewSerializer()
    proposaldeclineddetails = ProposalDeclinedDetailsSerializer()
    #
    assessor_mode = serializers.SerializerMethodField()
    can_edit_activities = serializers.SerializerMethodField()
    current_assessor = serializers.SerializerMethodField()
    assessor_data = serializers.SerializerMethodField()
    latest_referrals = ProposalReferralSerializer(many=True)
    allowed_assessors = EmailUserSerializer(many=True)
    approval_level_document = serializers.SerializerMethodField()
    application_type = serializers.CharField(source='application_type.name', read_only=True)
    region = serializers.CharField(source='region.name', read_only=True)
    district = serializers.CharField(source='district.name', read_only=True)
    #tenure = serializers.CharField(source='tenure.name', read_only=True)
    qaofficer_referrals = QAOfficerReferralSerializer(many=True)
    reversion_ids = serializers.SerializerMethodField()
    assessor_assessment=ProposalAssessmentSerializer(read_only=True)
    referral_assessments=ProposalAssessmentSerializer(read_only=True, many=True)
    fee_invoice_url = serializers.SerializerMethodField()
    #selected_trails_activities=serializers.SerializerMethodField()
    #selected_parks_activities=serializers.SerializerMethodField()
    #marine_parks_activities=serializers.SerializerMethodField()

    class Meta:
        model = Proposal
        fields = (
                'id',
                'application_type',
                'activity',
                'approval_level',
                'approval_level_document',
                'region',
                'district',
                'tenure',
                'title',
                'data',
                'schema',
                'customer_status',
                'processing_status',
                'review_status',
                #'hard_copy',
                'applicant',
                'org_applicant',
                'proxy_applicant',
                'submitter',
                'applicant_type',
                'assigned_officer',
                'assigned_approver',
                'previous_application',
                'get_history',
                'lodgement_date',
                'modified_date',
                'documents',
                'requirements',
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
                'proposed_issuance_approval',
                'proposed_decline_status',
                'proposaldeclineddetails',
                'permit',
                'reference',
                'lodgement_number',
                'lodgement_sequence',
                'can_officer_process',
                'proposal_type',
                'qaofficer_referrals',
                # tab field models
                'applicant_details',
                'other_details',
                'activities_land',
                'land_access',
                'land_access',
                'trail_activities',
                'trail_section_activities',
                'activities_marine',
                'land_parks',
                'marine_parks',
                'trails',
                'training_completed',
                'can_edit_activities',
                #Following 3 are variable to store selected parks and activities at frontend
                #'selected_parks_activities',
                #'selected_trails_activities',
                #'marine_parks_activities',
                'reversion_ids',
                'assessor_assessment',
                'referral_assessments',
                'fee_invoice_url',
                'fee_paid'
                )
        read_only_fields=('documents','requirements')

    def get_approval_level_document(self,obj):
        if obj.approval_level_document is not None:
            return [obj.approval_level_document.name,obj.approval_level_document._file.url]
        else:
            return obj.approval_level_document

    def get_assessor_mode(self,obj):
        # TODO check if the proposal has been accepted or declined
        request = self.context['request']
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        return {
            'assessor_mode': True,
            'has_assessor_mode': obj.has_assessor_mode(user),
            'assessor_can_assess': obj.can_assess(user),
            'assessor_level': 'assessor',
            'assessor_box_view': obj.assessor_comments_view(user)
        }

    def get_can_edit_activities(self,obj):
        request = self.context['request']
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        return obj.can_edit_activities(user)

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

    def get_reversion_ids(self,obj):
        return obj.reversion_ids[:5]

    def get_fee_invoice_url(self,obj):
        return '/cols/payments/invoice-pdf/{}'.format(obj.fee_invoice_reference) if obj.fee_paid else None

    def get_selected_parks_activities(self,obj):
        return []

    def get_selected_trails_activities(self,obj):
        return []

    def get_marine_parks_activities(self,obj):
        return []


class ReferralProposalSerializer(InternalProposalSerializer):
    def get_assessor_mode(self,obj):
        # TODO check if the proposal has been accepted or declined
        request = self.context['request']
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        try:
            referral = Referral.objects.get(proposal=obj,referral=user)
        except:
            referral = None
        return {
            'assessor_mode': True,
            'assessor_can_assess': referral.can_assess_referral(user) if referral else None,
            'assessor_level': 'referral',
            'assessor_box_view': obj.assessor_comments_view(user)
        }

class ReferralSerializer(serializers.ModelSerializer):
    processing_status = serializers.CharField(source='get_processing_status_display')
    latest_referrals = ProposalReferralSerializer(many=True)
    can_be_completed = serializers.BooleanField()
    can_process=serializers.SerializerMethodField()
    referral_assessment=ProposalAssessmentSerializer(read_only=True)


    class Meta:
        model = Referral
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(ReferralSerializer, self).__init__(*args, **kwargs)
        self.fields['proposal'] = ReferralProposalSerializer(context={'request':self.context['request']})

    def get_can_process(self,obj):
        request = self.context['request']
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        return obj.can_process(user)

class ProposalUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')
    class Meta:
        model = ProposalUserAction
        fields = '__all__'

class ProposalLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()
    class Meta:
        model = ProposalLogEntry
        fields = '__all__'
        read_only_fields = (
            'customer',
        )

    def get_documents(self,obj):
        return [[d.name,d._file.url] for d in obj.documents.all()]

class SendReferralSerializer(serializers.Serializer):
    #email = serializers.EmailField()
    email_group = serializers.CharField()
    text = serializers.CharField(allow_blank=True)

class DTReferralSerializer(serializers.ModelSerializer):
    processing_status = serializers.CharField(source='proposal.get_processing_status_display')
    referral_status = serializers.CharField(source='get_processing_status_display')
    proposal_lodgement_date = serializers.CharField(source='proposal.lodgement_date')
    proposal_lodgement_number = serializers.CharField(source='proposal.lodgement_number')
    submitter = serializers.SerializerMethodField()
    region = serializers.CharField(source='region.name', read_only=True)
    #referral = EmailUserSerializer()
    referral = serializers.CharField(source='referral_group.name')
    document = serializers.SerializerMethodField()
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
            'proposal',
            'can_be_processed',
            'referral',
            'proposal_lodgement_date',
            'proposal_lodgement_number',
            'referral_text',
            'document',
        )

    def get_submitter(self,obj):
        return EmailUserSerializer(obj.proposal.submitter).data

    def get_document(self,obj):
        docs =  [[d.name,d._file.url] for d in obj.referral_documents.all()]
        return docs[0] if docs else None

class RequirementDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequirementDocument
        fields = ('id', 'name', '_file')
        #fields = '__all__'

class ProposalRequirementSerializer(serializers.ModelSerializer):
    due_date = serializers.DateField(input_formats=['%d/%m/%Y'],required=False,allow_null=True)
    can_referral_edit=serializers.SerializerMethodField()
    requirement_documents = RequirementDocumentSerializer(many=True, read_only=True)
    class Meta:
        model = ProposalRequirement
        fields = (
            'id',
            'due_date',
            'free_requirement',
            'standard_requirement',
            'standard','order',
            'proposal',
            'recurrence',
            'recurrence_schedule',
            'recurrence_pattern',
            'requirement',
            'is_deleted',
            'copied_from',
            'referral_group',
            'can_referral_edit',
            'requirement_documents'
        )
        read_only_fields = ('order','requirement', 'copied_from')

    def get_can_referral_edit(self,obj):
        request = self.context['request']
        user = request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
        return obj.can_referral_edit(user)

class ProposalStandardRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalStandardRequirement
        fields = ('id','code','text')

class ProposedApprovalSerializer(serializers.Serializer):
    expiry_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    start_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    details = serializers.CharField()
    cc_email = serializers.CharField(required=False,allow_null=True)

class PropedDeclineSerializer(serializers.Serializer):
    reason = serializers.CharField()
    cc_email = serializers.CharField(required=False)

class OnHoldSerializer(serializers.Serializer):
    comment = serializers.CharField()


class AmendmentRequestSerializer(serializers.ModelSerializer):
    #reason = serializers.SerializerMethodField()

    class Meta:
        model = AmendmentRequest
        fields = '__all__'

    #def get_reason (self,obj):
        #return obj.get_reason_display()
        #return obj.reason.reason

class AmendmentRequestDisplaySerializer(serializers.ModelSerializer):
    reason = serializers.SerializerMethodField()

    class Meta:
        model = AmendmentRequest
        fields = '__all__'

    def get_reason (self,obj):
        #return obj.get_reason_display()
        return obj.reason.reason if obj.reason else None


class SearchKeywordSerializer(serializers.Serializer):
    number = serializers.CharField()
    id = serializers.IntegerField()
    type = serializers.CharField()
    applicant = serializers.CharField()
    #text = serializers.CharField(required=False,allow_null=True)
    text = serializers.JSONField(required=False)

class SearchReferenceSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    type = serializers.CharField()

class VehicleSerializer(serializers.ModelSerializer):
    access_type= AccessTypeSerializer()
    rego_expiry=serializers.DateField(format="%d/%m/%Y")
    class Meta:
        model = Vehicle
        fields = ('id', 'capacity', 'rego', 'license', 'access_type', 'rego_expiry', 'proposal')

class VesselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vessel
        fields = '__all__'

class SaveVehicleSerializer(serializers.ModelSerializer):
    #access_type= AccessTypeSerializer()
    rego_expiry = serializers.DateField(input_formats=['%d/%m/%Y'], allow_null=True)
    class Meta:
        model = Vehicle
        fields = ('id', 'capacity', 'rego', 'license', 'access_type', 'rego_expiry', 'proposal')

