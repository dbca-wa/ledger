from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from disturbance.components.proposals.models import (
                                    ProposalType,
                                    Proposal
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

class EmailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = ('id','email','first_name','last_name','title','organisation')

class BaseProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = '__all__'

class DTProposalSerializer(BaseProposalSerializer):
    submitter = EmailUserSerializer()

class ProposalSerializer(BaseProposalSerializer):
    pass
