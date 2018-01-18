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

    class Meta:
        model = Compliance
        fields = (
            'id',
            'proposal',
            'due_date',
            'processing_status',
            'regions',
            'activity',
            'title',
            'holder',
            'assigned_to',
            'approval',
        )
