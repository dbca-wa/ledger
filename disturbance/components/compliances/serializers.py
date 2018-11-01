from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from disturbance.components.compliances.models import (
    Compliance, ComplianceUserAction, ComplianceLogEntry, ComplianceAmendmentRequest, ComplianceAmendmentReason
)
from rest_framework import serializers


class EmailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = ('id','email','first_name','last_name','title','organisation')

class ComplianceSerializer(serializers.ModelSerializer):
    regions = serializers.CharField(source='proposal.region')
    activity = serializers.CharField(source='proposal.activity')
    title = serializers.CharField(source='proposal.title')
    holder = serializers.CharField(source='proposal.applicant.name')
    processing_status = serializers.CharField(source='get_processing_status_display')
    customer_status = serializers.CharField(source='get_customer_status_display')
    submitter = serializers.SerializerMethodField(read_only=True)
    documents = serializers.SerializerMethodField()
    #submitter = serializers.CharField(source='submitter.get_full_name')
    submitter = serializers.SerializerMethodField(read_only=True)
    allowed_assessors = EmailUserSerializer(many=True)
    #assigned_to = serializers.CharField(source='assigned_to.get_full_name')
    assigned_to = serializers.SerializerMethodField(read_only=True)
    requirement = serializers.CharField(source='requirement.requirement', required=False, allow_null=True)
    approval_lodgement_number = serializers.SerializerMethodField()


    class Meta:
        model = Compliance
        fields = (
            'id',
            'proposal',
            'due_date',
            'processing_status',
            'customer_status',
            'regions',
            'activity',
            'title',
            'text',
            'holder',
            'assigned_to',
            'approval',
            'documents',
            'requirement',
            'can_user_view',
            'reference',
            'lodgement_number',
            'lodgement_date',
            'submitter',
            'allowed_assessors',
            'lodgement_date',
            'approval_lodgement_number'

        )

    def get_documents(self,obj):
        return [[d.name,d._file.url,d.can_delete,d.id] for d in obj.documents.all()]

    def get_approval_lodgement_number(self,obj):
        return obj.approval.lodgement_number

    def get_assigned_to(self,obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name()
        return None

    def get_submitter(self,obj):
        if obj.submitter:
            return obj.submitter.get_full_name()
        return None

class SaveComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = (
            'id',
            'title',
            'text',

        )

class ComplianceActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')
    class Meta:
        model = ComplianceUserAction
        fields = '__all__'

class ComplianceCommsSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()
    class Meta:
        model = ComplianceLogEntry
        fields = '__all__'
    def get_documents(self,obj):
        return [[d.name,d._file.url] for d in obj.documents.all()]

class ComplianceAmendmentRequestSerializer(serializers.ModelSerializer):
    #reason = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceAmendmentRequest
        fields = '__all__'

    # def get_reason (self,obj):
    #     return obj.get_reason_display()

class CompAmendmentRequestDisplaySerializer(serializers.ModelSerializer):
    reason = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceAmendmentRequest
        fields = '__all__'

    def get_reason (self,obj):
        #return obj.get_reason_display()
        return obj.reason.reason if obj.reason else None

