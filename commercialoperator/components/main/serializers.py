from rest_framework import serializers
from commercialoperator.components.main.models import CommunicationsLogEntry, Region, District, Tenure, ApplicationType, ActivityMatrix, AccessType, Park, Trail, Activity, ActivityCategory, Section, Zone, RequiredDocument, Question, GlobalSettings #, ParkPrice
from commercialoperator.components.proposals.models import  ProposalParkActivity
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

class ParkSerializer2(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()

    class Meta:
        model = Park
        fields=('id', 'label', 'can_edit')

    def get_label(self, obj):
        return obj.name

    def get_can_edit(self, obj):
        #proposal = self.context['request'].GET.get('proposal')
        #activities = ProposalParkActivity.objects.filter(proposal_park__park=obj.id, proposal_park__proposal=proposal)
        #return True if activities else False
        return True

class DistrictSerializer2(serializers.ModelSerializer):
    pk = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    children = ParkSerializer2(many=True, read_only=True, source='land_parks')

    class Meta:
        model = District
        #fields = ('id', 'name', 'land_parks', 'marine_parks')
        fields = ('pk', 'id', 'label', 'children')

    def get_pk(self, obj):
        return obj.id

    def get_id(self, obj):
        return obj.code

    def get_label(self, obj):
        return obj.name

class RegionSerializer2(serializers.ModelSerializer):
    pk = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    children = DistrictSerializer2(many=True, read_only=True, source='districts')

    class Meta:
        model = Region
        fields = ('pk', 'id', 'label', 'children')

    def get_pk(self, obj):
        return obj.id

    def get_id(self, obj):
        return obj.name

    def get_label(self, obj):
        return obj.name


class AccessTypeSerializer2(serializers.ModelSerializer):
    pk = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    class Meta:
        model = AccessType
        fields = ('pk', 'id', 'label', 'visible')

    def get_pk(self, obj):
        return obj.id

    def get_id(self, obj):
        return obj.name

    def get_label(self, obj):
        return obj.name

class ActivitySerializer2(serializers.ModelSerializer):
    label = serializers.SerializerMethodField()
    class Meta:
        model = Activity
        fields = ('id','label')

    def get_label(self, obj):
        return obj.name


class ActivityCategorySerializer2(serializers.ModelSerializer):
    pk = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    children = ActivitySerializer2(many=True, read_only=True, source='activities')

    class Meta:
        model = ActivityCategory
        fields = ('pk', 'id', 'label','children')

    def get_pk(self, obj):
        return obj.id

    def get_id(self, obj):
        return obj.name

    def get_label(self, obj):
        return obj.name

class TrailSerializer2(serializers.ModelSerializer):
    pk = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    sections=SectionSerializer(many=True)
    allowed_activities=ActivitySerializer(many=True)
    class Meta:
        model = Trail
        fields = ('pk', 'id', 'label', 'can_edit', 'code', 'section_ids', 'sections', 'allowed_activities')

    def get_pk(self, obj):
        return obj.id

    def get_id(self, obj):
        return obj.name

    def get_label(self, obj):
        return obj.name

    def get_can_edit(self, obj):
        #proposal = self.context['request'].GET.get('proposal')
        #activities = ProposalParkActivity.objects.filter(proposal_park__park=obj.id, proposal_park__proposal=proposal)
        #return True if activities else False
        return True




class AccessTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessType

    class Meta:
        model = AccessType
        fields = ('id', 'name', 'visible')


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


class LandActivityTabSerializer(serializers.Serializer):
    land_parks = RegionSerializer2(many=True, read_only=True, source='regions')
    access_types = AccessTypeSerializer2(many=True, read_only=True)
    land_activity_types = ActivitySerializer2(many=True, read_only=True)
    marine_activity_types = ActivitySerializer2(many=True, read_only=True)
    trails = TrailSerializer2(many=True, read_only=True)
    marine_activities = ActivityCategorySerializer2(many=True, read_only=True)


class BookingSettlementReportSerializer(serializers.Serializer):
    date = serializers.DateTimeField(input_formats=['%d/%m/%Y'])


class OracleSerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=['%d/%m/%Y','%Y-%m-%d'])
    override = serializers.BooleanField(default=False)


