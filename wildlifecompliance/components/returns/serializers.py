from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from wildlifecompliance.components.returns.models import (
    Return,
    ReturnType
)
from rest_framework import serializers

class ReturnSerializer(serializers.ModelSerializer):
    # activity = serializers.CharField(source='application.activity')
    processing_status = serializers.CharField(source='get_processing_status_display')

    class Meta:
        model = Return 
        fields = (
            'id',
            'application',
            'due_date',
            'processing_status',
            'assigned_to',
            'licence',
            'resources',
            'table'
        )

class ReturnTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ReturnType
        fields=(
            'id',
            'resources'
            )
