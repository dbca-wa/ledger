from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from disturbance.components.proposals.models import (
                                    ProposalType,
                                )
from rest_framework import serializers

class ProposalTypeSerializer(serializers.ModelSerializer):
    activities = serializers.SerializerMethodField()
    class Meta:
        model = ProposalType
        fields = (
            'id',
            'schema',
            'activities'
        )

    def get_activities(self,obj):
        return obj.activities.names()
