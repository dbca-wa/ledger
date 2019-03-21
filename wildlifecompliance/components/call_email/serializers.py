from wildlifecompliance.components.call_email.models import (
    CallEmail,
    Classification
	)
from wildlifecompliance.components.applications.serializers import BaseApplicationSerializer
from rest_framework import serializers


class ClassificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Classification
        fields = (
            'id',
            'name',
        )

class CallEmailSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    classification = ClassificationSerializer(read_only=True)
    
    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'classification'
        )

