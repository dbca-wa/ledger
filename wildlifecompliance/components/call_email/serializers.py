import traceback
from wildlifecompliance.components.call_email.models import (
    CallEmail,
    Classification
	)
from wildlifecompliance.components.applications.serializers import BaseApplicationSerializer
from rest_framework import serializers
from django.core.exceptions import ValidationError


class ClassificationSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(source='get_name_display') 

    class Meta:
        model = Classification
        fields = (
            'id',
            'name',
        )
        read_only_fields = ('id', 'name', )


class CreateCallEmailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'classification',
            'number',
            'caller',
            'assigned_to',
        )
        read_only_fields = ('id', )


class CallEmailSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    classification = ClassificationSerializer()
    lodgement_date = serializers.CharField(
            source='lodged_on')
    
    class Meta:
        model = CallEmail
        fields = (
            'id',
            'status',
            'classification',
            'lodgement_date',
            'number',
            'caller',
            'assigned_to',
        )
        read_only_fields = ('id', )
