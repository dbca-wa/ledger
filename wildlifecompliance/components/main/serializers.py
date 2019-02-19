from rest_framework import serializers
from wildlifecompliance.components.main.models import CommunicationsLogEntry
from ledger.accounts.models import EmailUser


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
            'type',
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
