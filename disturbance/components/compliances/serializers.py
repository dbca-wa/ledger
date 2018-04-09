from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from disturbance.components.compliances.models import (
    Compliance 
)
from rest_framework import serializers

class ComplianceSerializer(serializers.ModelSerializer):
    regions = serializers.CharField(source='proposal.region')
    activity = serializers.CharField(source='proposal.activity')
    title = serializers.CharField(source='proposal.title')
    holder = serializers.CharField(source='proposal.applicant.name')
    processing_status = serializers.CharField(source='get_processing_status_display')
    customer_status = serializers.CharField(source='get_customer_status_display')
    documents = serializers.SerializerMethodField()

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
            'lodgement_date'
        )

    def get_documents(self,obj):
        return [[d.name,d._file.url] for d in obj.documents.all()]

class SaveComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = (
            'id',
            'title',
            'text',
            
          
        )