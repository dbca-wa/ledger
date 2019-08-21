from rest_framework import serializers
from wildlifecompliance.components.main.models import CommunicationsLogEntry
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.main.models import WeakLinks


class CommunicationLogEntrySerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(
        queryset=EmailUser.objects.all(), required=False)
    documents = serializers.SerializerMethodField()

    class Meta:
        model = CommunicationsLogEntry
        fields = (
            'id',
            'customer',
            'to',
            'fromm',
            'cc',
            'log_type',
            'reference',
            'subject'
            'text',
            'created',
            'staff',
            'application'
            'documents'
        )

    def get_documents(self, obj):
        return [[d.name, d._file.url] for d in obj.documents.all()]


class SearchKeywordSerializer(serializers.Serializer):
    number = serializers.CharField()
    record_id = serializers.IntegerField()
    record_type = serializers.CharField()
    applicant = serializers.CharField()
    text = serializers.JSONField(required=False)
    licence_document = serializers.CharField(
        source='licence_document._file.url',
        required=False
    )

# to return object description fields for drop-down list vuew
class SearchWeakLinksSerializer(serializers.Serializer):
    #number = serializers.CharField()
    #record_id = serializers.IntegerField()
    #record_type = serializers.CharField()
    #applicant = serializers.CharField()
    #text = serializers.JSONField(required=False)
    pass


class SearchReferenceSerializer(serializers.Serializer):
    url_string = serializers.CharField()
