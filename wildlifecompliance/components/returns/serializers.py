from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from wildlifecompliance.components.returns.models import (
    Return
)
from rest_framework import serializers

class ReturnSerializer(serializers.ModelSerializer):
    regions = serializers.CharField(source='application.region')
    activity = serializers.CharField(source='application.activity')
    title = serializers.CharField(source='application.title')
    holder = serializers.CharField(source='application.applicant.name')
    processing_status = serializers.CharField(source='get_processing_status_display')

    class Meta:
        model = Return 
        fields = (
            'id',
            'application',
            'due_date',
            'processing_status',
            'regions',
            'activity',
            'title',
            'holder',
            'assigned_to',
            'licence',
        )
