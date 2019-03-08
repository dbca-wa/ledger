from wildlifecompliance.components.call_email.models import (
    CallEmail,
	)
from wildlifecompliance.components.applications.serializers import BaseApplicationSerializer
from rest_framework import serializers


class CallEmailSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'classification'
        )


