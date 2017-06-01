from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from disturbance.models import (   
                                    ProposalType,
                                )
from rest_framework import serializers

class ProposalTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalType
        fields = (
            'id',
            'schema',
            'activities'
        )
