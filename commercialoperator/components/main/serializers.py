from rest_framework import serializers
from commercialoperator.components.main.models import CommunicationsLogEntry, Region, District, Tenure, ApplicationType, ActivityMatrix, AccessType, Park, Trail, Activity, ActivityCategory, Section, Zone
from ledger.accounts.models import EmailUser
#from commercialoperator.components.proposals.serializers import ProposalTypeSerializer 

class CommunicationLogEntrySerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=EmailUser.objects.all(),required=False)
    documents = serializers.SerializerMethodField()
    class Meta:
        model = CommunicationsLogEntry
        fields = (
            'id',
            'customer',
            'to',
            'fromm',
            'cc',
            'type',
            'reference',
            'subject'
            'text',
            'created',
            'staff',
            'proposal'
            'documents'
        )

    def get_documents(self,obj):
        return [[d.name,d._file.url] for d in obj.documents.all()]

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ('id', 'name', 'visible')

class ParkSerializer(serializers.ModelSerializer):
    zones=ZoneSerializer(many=True)
    class Meta:
        model = Park
        #fields = '__all__'
        fields=('id', 'zones', 'name', 'code', 'park_type', 'allowed_activities', 'zone_ids')

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name', 'visible')
        

class DistrictSerializer(serializers.ModelSerializer):
    land_parks = ParkSerializer(many=True)
    marine_parks = ParkSerializer(many=True)
    class Meta:
        model = District
        fields = ('id', 'name', 'code', 'land_parks', 'marine_parks')



class RegionSerializer(serializers.ModelSerializer):
    districts = DistrictSerializer(many=True)
    class Meta:
        model = Region
        fields = ('id', 'name','forest_region', 'districts')



class ActivityMatrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityMatrix
        fields = ('id', 'name', 'description', 'version', 'ordered', 'schema')


#class ActivitySerializer(serializers.ModelSerializer):
#    class Meta:
#        model = Activity
#        #ordering = ('order', 'name')
#        fields = ('id', 'name', 'application_type')


class TenureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenure
        fields = ('id', 'name', 'application_type')


class ApplicationTypeSerializer(serializers.ModelSerializer):
    #regions = RegionSerializer(many=True)
    #activity_app_types = ActivitySerializer(many=True)
    tenure_app_types = TenureSerializer(many=True)
    class Meta:
        model = ApplicationType
        #fields = ('id', 'name', 'activity_app_types', 'tenure_app_types')
        fields = ('id', 'name', 'tenure_app_types')


class AccessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessType
        fields = ('id', 'name', 'visible')

# class VehicleSerializer(serializers.ModelSerializer):
#     access_type= AccessTypeSerializer()
#     rego_expiry=serializers.DateField(format="%d/%m/%Y")
#     class Meta:
#         model = Vehicle
#         fields = ('id', 'capacity', 'rego', 'license', 'access_type', 'rego_expiry')

# class SaveVehicleSerializer(serializers.ModelSerializer):
#     #access_type= AccessTypeSerializer()
#     rego_expiry = serializers.DateField(input_formats=['%d/%m/%Y'], allow_null=True)
#     class Meta:
#         model = Vehicle
#         fields = ('id', 'capacity', 'rego', 'license', 'access_type', 'rego_expiry')

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('id','name')

class ActivityCategorySerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(many=True)
    class Meta:
        model = ActivityCategory
        fields = ('id', 'name','activities')

class TrailSerializer(serializers.ModelSerializer):
    sections=SectionSerializer(many=True)
    allowed_activities=ActivitySerializer(many=True)
    class Meta:
        model = Trail
        fields = ('id', 'name', 'code', 'section_ids', 'sections', 'allowed_activities')