from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from disturbance.components.compliances.models import (
    Compliance, ComplianceUserAction, ComplianceLogEntry, ComplianceAmendmentRequest
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
    documents = serializers.SerializerMethodField()
    submitter = serializers.CharField(source='submitter.get_full_name')
    allowed_assessors = EmailUserSerializer(many=True)
    assigned_to = serializers.CharField(source='assigned_to.get_full_name')
    requirement = serializers.CharField(source='requirement.requirement')
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
            'lodgement_date',
            'submitter',
            'allowed_assessors',
            'lodgement_date',
            'approval_lodgement_number'

        )

    def get_documents(self,obj):
        return [[d.name,d._file.url, d.id] for d in obj.documents.all()]

    def get_approval_lodgement_number(self,obj):
        return obj.approval.lodgement_number

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
    reason = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceAmendmentRequest
        fields = '__all__'
    
    def get_reason (self,obj):
        return obj.get_reason_display()

