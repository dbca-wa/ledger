import traceback

from rest_framework.fields import CharField
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometryField

from ledger.accounts.models import EmailUser, Address
from wildlifecompliance.components.inspection.models import (
    Inspection,
    InspectionUserAction,
    InspectionCommsLogEntry,
    # InspectionType,
    )
from wildlifecompliance.components.main.models import get_related_items
from wildlifecompliance.components.main.serializers import CommunicationLogEntrySerializer
from wildlifecompliance.components.users.serializers import (
    ComplianceUserDetailsOptimisedSerializer,
    CompliancePermissionGroupMembersSerializer
)
from rest_framework import serializers
from django.core.exceptions import ValidationError
from wildlifecompliance.components.main.fields import CustomChoiceField

from wildlifecompliance.components.users.serializers import UserAddressSerializer


class InspectionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Inspection
        fields = '__all__'


class SaveInspectionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Inspection
        fields = (
                'title',
                'details'
                )

#class SaveInspectionSerializer(serializers.ModelSerializer):
 #   title = models.CharField(max_length=200, blank=True, null=True)
  #  details = models.TextField(blank=True, null=True)
   # number = models.CharField(max_length=50, blank=True, null=True)
    #planned_for_date = models.DateField(null=True)
    #planned_for_time = models.CharField(max_length=20, blank=True, null=True)


#class InspectionTypeSerializer(serializers.ModelSerializer):
 #   class Meta:
  #      model = InspectionType
   #     fields = '__all__'

class InspectionUserActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')

    class Meta:
        model = InspectionUserAction
        fields = '__all__'


class InspectionCommsLogEntrySerializer(CommunicationLogEntrySerializer):
    documents = serializers.SerializerMethodField()

    class Meta:
        model = InspectionCommsLogEntry
        fields = '__all__'
        read_only_fields = (
            'customer',
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]
