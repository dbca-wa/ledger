from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from ledger.licence.models import LicenceType
from wildlifecompliance.components.licences.models import (
    Licence,WildlifeLicenceClass,WildlifeLicenceActivityType,WildlifeLicenceActivity
)
from wildlifecompliance.components.organisations.models import (
                                Organisation
                            )
from rest_framework import serializers

class LicenceSerializer(serializers.ModelSerializer):
    applicant = serializers.CharField(source='applicant.name')
    licence_document = serializers.CharField(source='licence_document._file.url')
    status = serializers.CharField(source='get_status_display')
    class Meta:
        model = Licence
        fields = (
            'id',
            'licence_document',
            'replaced_by',
            'current_application',
            'activity',
            'region',
            'tenure',
            'title',
            'renewal_sent',
            'issue_date',
            'original_issue_date',
            'start_date',
            'expiry_date',
            'surrender_details',
            'suspension_details',
            'applicant',
            'extracted_fields',
            'status'
        )

class DefaultActivitySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    class Meta:
        model = WildlifeLicenceActivity
        fields = (
            'id',
            'name',
            'base_application_fee',
            'base_licence_fee',
            'short_name'
        ) 


class DefaultActivityTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    activity = DefaultActivitySerializer(many=True,read_only=True)
    class Meta:
        model = WildlifeLicenceActivityType
        fields = (
            'id',
            'name',
            'activity',
            'short_name',
            'not_for_organisation'
        ) 

class LicenceClassSerializer(serializers.ModelSerializer):
    class_status = serializers.SerializerMethodField()
    activity_type = DefaultActivityTypeSerializer(many=True,read_only=True)
    class Meta:
        model = WildlifeLicenceClass
        fields = (
            'id',
            'name',
            'short_name',
            'class_status',
            'activity_type'
            
        )
    def get_class_status(self,obj):
        return obj.get_licence_class_status_display()
