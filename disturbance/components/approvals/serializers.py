from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from disturbance.components.approvals.models import (
    Approval,
    ApprovalLogEntry,
    ApprovalUserAction
)
from disturbance.components.organisations.models import (
                                Organisation
                            )
from disturbance.components.main.serializers import CommunicationLogEntrySerializer 
from rest_framework import serializers


class EmailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = ('id','email','first_name','last_name','title','organisation')


class ApprovalSerializer(serializers.ModelSerializer):
    applicant = serializers.CharField(source='applicant.name')
    applicant_id = serializers.ReadOnlyField(source='applicant.id')
    licence_document = serializers.CharField(source='licence_document._file.url')
    renewal_document = serializers.CharField(source='renewal_document._file.url')
    status = serializers.CharField(source='get_status_display')
    allowed_assessors = EmailUserSerializer(many=True)
    
    class Meta:
        model = Approval
        fields = (
            'id',
            'licence_document',
            'replaced_by',
            'current_proposal',
            'activity',
            'region',
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
            'extracted_fields',
            'status',
            'reference',
            'can_reissue',
            'allowed_assessors',
            'cancellation_date',
            'cancellation_details',
            'applicant_id',
            'can_action',
            'set_to_cancel',
            'set_to_surrender',
            'set_to_suspend'
        )

class ApprovalCancellationSerializer(serializers.Serializer):
    cancellation_date = serializers.DateField(input_formats=['%d/%m/%Y'])    
    cancellation_details = serializers.CharField()
    
class ApprovalSuspensionSerializer(serializers.Serializer):
    from_date = serializers.DateField(input_formats=['%d/%m/%Y'])
    to_date = serializers.DateField(input_formats=['%d/%m/%Y'])
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