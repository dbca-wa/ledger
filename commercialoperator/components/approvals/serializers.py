from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from commercialoperator.components.proposals.serializers import ProposalSerializer, InternalProposalSerializer
from commercialoperator.components.main.serializers import ApplicationTypeSerializer
from commercialoperator.components.approvals.models import (
    Approval,
    ApprovalLogEntry,
    ApprovalUserAction
)
from commercialoperator.components.organisations.models import (
    Organisation
)
from commercialoperator.components.main.serializers import CommunicationLogEntrySerializer
from rest_framework import serializers


class EmailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = ('id','email','first_name','last_name','title','organisation')

from commercialoperator.components.proposals.serializers import ProposalSerializer
class ApprovalSerializer(serializers.ModelSerializer):
    #applicant = serializers.CharField(source='applicant.name')
    applicant = serializers.SerializerMethodField(read_only=True)
    applicant_type = serializers.SerializerMethodField(read_only=True)
    applicant_id = serializers.SerializerMethodField(read_only=True)
    #applicant_id = serializers.ReadOnlyField(source='applicant.id')
    licence_document = serializers.CharField(source='licence_document._file.url')
    #renewal_document = serializers.CharField(source='renewal_document._file.url')
    renewal_document = serializers.SerializerMethodField(read_only=True)
    status = serializers.CharField(source='get_status_display')
    allowed_assessors = EmailUserSerializer(many=True)
    region = serializers.CharField(source='current_proposal.region.name')
    district = serializers.CharField(source='current_proposal.district.name', allow_null=True)
    #tenure = serializers.CharField(source='current_proposal.tenure.name')
    activity = serializers.CharField(source='current_proposal.activity')
    title = serializers.CharField(source='current_proposal.title')
    #current_proposal = InternalProposalSerializer(many=False)
    #application_type = ApplicationTypeSerializer(many=True)
    application_type = serializers.SerializerMethodField(read_only=True)
    can_renew = serializers.SerializerMethodField()
    can_extend = serializers.SerializerMethodField()

    class Meta:
        model = Approval
        fields = (
            'id',
            'lodgement_number',
            'licence_document',
            'replaced_by',
            'current_proposal',
            'activity',
            'region',
            'district',
            'tenure',
            'title',
            'renewal_document',
            'renewal_sent',
            'issue_date',
            'original_issue_date',
            'start_date',
            'expiry_date',
            'surrender_details',
            'suspension_details',
            'applicant',
            'applicant_type',
            'applicant_id',
            'extracted_fields',
            'status',
            'reference',
            'can_reissue',
            'allowed_assessors',
            'cancellation_date',
            'cancellation_details',
            'can_action',
            'set_to_cancel',
            'set_to_surrender',
            'set_to_suspend',
            'can_renew',
            'can_extend',
            'can_amend',
            'can_reinstate',
            'application_type'
        )
        # the serverSide functionality of datatables is such that only columns that have field 'data' defined are requested from the serializer. We
        # also require the following additional fields for some of the mRender functions
        datatables_always_serialize = (
            'id',
            'activity',
            'region',
            'title',
            'status',
            'reference',
            'lodgement_number',
            'licence_document',
            'start_date',
            'expiry_date',
            'applicant',
            'can_reissue',
            'can_action',
            'can_reinstate',
            'can_amend',
            'can_renew',
            'can_extend',
            'set_to_cancel',
            'set_to_suspend',
            'set_to_surrender',
            'current_proposal',
            'renewal_document',
            'renewal_sent',
            'allowed_assessors',
            'application_type'
        )

    def get_renewal_document(self,obj):
        if obj.renewal_document and obj.renewal_document._file:
            return obj.renewal_document._file.url
        return None

    def get_application_type(self,obj):
        if obj.current_proposal.application_type:
            return obj.current_proposal.application_type.name
        return None

    def get_applicant(self,obj):
        return obj.applicant.name if isinstance(obj.applicant, Organisation) else obj.applicant

    def get_applicant_type(self,obj):
        return obj.applicant_type

    def get_applicant_id(self,obj):
        return obj.applicant_id

    def get_can_renew(self,obj):
        return obj.can_renew

    def get_can_extend(self,obj):
        return obj.can_extend


class ApprovalExtendSerializer(serializers.Serializer):
    extend_details = serializers.CharField()

class ApprovalCancellationSerializer(serializers.Serializer):
    cancellation_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    cancellation_details = serializers.CharField()

class ApprovalSuspensionSerializer(serializers.Serializer):
    from_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    to_date = serializers.DateField(input_formats=['%d/%m/%Y'], required=False, allow_null=True)
    suspension_details = serializers.CharField()

class ApprovalSurrenderSerializer(serializers.Serializer):
    surrender_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    surrender_details = serializers.CharField()

class ApprovalUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')
    class Meta:
        model = ApprovalUserAction
        fields = '__all__'

class ApprovalLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()
    class Meta:
        model = ApprovalLogEntry
        fields = '__all__'
        read_only_fields = (
            'customer',
        )

    def get_documents(self,obj):
        return [[d.name,d._file.url] for d in obj.documents.all()]
