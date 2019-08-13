from rest_framework import serializers
from commercialoperator.components.main.models import CommunicationsLogEntry, Region, District, Tenure, ApplicationType, ActivityMatrix, AccessType, Park, Trail, Activity, ActivityCategory, Section, Zone, RequiredDocument, Question, GlobalSettings #, ParkPrice
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


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', 'name', 'visible', 'doc_url')

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('id','name')


class ZoneSerializer(serializers.ModelSerializer):
    allowed_activities=ActivitySerializer(many=True)
    class Meta:
        model = Zone
        fields = ('id', 'name', 'visible', 'allowed_activities')

class ParkFilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Park
        fields=('id', 'name', 'park_type')

class ParkSerializer(serializers.ModelSerializer):
    zones=ZoneSerializer(many=True)
    class Meta:
        model = Park
        fields=('id', 'zones', 'name', 'code', 'park_type', 'allowed_activities', 'zone_ids', 'adult_price', 'child_price', 'oracle_code')

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
    #tenure_app_types = TenureSerializer(many=True)
    class Meta:
        model = ApplicationType
        #fields = ('id', 'name', 'activity_app_types', 'tenure_app_types')
        #fields = ('id', 'name', 'tenure_app_types')
        fields = '__all__'
        #extra_fields = ['pizzas']


class GlobalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSettings
        fields = ('key', 'value')


class AccessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessType
        fields = ('id', 'name', 'visible')


class RequiredDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequiredDocument
        fields = ('id', 'park','activity', 'question')


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


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('id', 'question_text', 'answer_one', 'answer_two', 'answer_three', 'answer_four','correct_answer', 'correct_answer_value')


class BookingSettlementReportSerializer(serializers.Serializer):
    date = serializers.DateTimeField(input_formats=['%d/%m/%Y'])


class OracleSerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=['%d/%m/%Y','%Y-%m-%d'])
    override = serializers.BooleanField(default=False)


