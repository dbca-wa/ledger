from django.conf import settings
from ledger.accounts.models import EmailUser,Address
from disturbance.components.proposals.models import (
                                    ProposalType,
                                    Proposal,
                                    ProposalUserAction,
                                    ProposalLogEntry,
                                )
from disturbance.components.organisations.models import (
                                Organisation
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
    readonly = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Proposal
        fields = (
                'id',
                'activity',
                'title',
                'region',
                'data',
                'schema',
                'customer_status',
                'processing_status',
                'review_status',
                'hard_copy',
                'applicant',
                'proxy_applicant',
                'submitter',
                'assigned_officer',
                'previous_application',
                'lodgement_date',
                'documents',
                'requirements',
                'readonly'
                )
        read_only_fields=('documents',)

    def get_readonly(self,obj):
        return False

    def get_processing_status(self,obj):
        return obj.get_processing_status_display()

    def get_review_status(self,obj):
        return obj.get_review_status_display()

    def get_customer_status(self,obj):
        return obj.get_customer_status_display()

class DTProposalSerializer(BaseProposalSerializer):
    submitter = EmailUserSerializer()
    applicant = serializers.CharField(source='applicant.organisation.name')
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)

class ProposalSerializer(BaseProposalSerializer):
    submitter = serializers.CharField(source='submitter.get_full_name')
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)

class SaveProposalSerializer(BaseProposalSerializer):
    pass

class ApplicantSerializer(serializers.ModelSerializer):
    from disturbance.components.organisations.serializers import OrganisationAddressSerializer
    address = OrganisationAddressSerializer()
    class Meta:
        model = Organisation
        fields = (
                    'id',
                    'name',
                    'abn',
                    'address',
                    'email',
                    'phone_number',
                )

class InternalProposalSerializer(BaseProposalSerializer):
    applicant = ApplicantSerializer()
    processing_status = serializers.SerializerMethodField(read_only=True)
    review_status = serializers.SerializerMethodField(read_only=True)
    customer_status = serializers.SerializerMethodField(read_only=True)
    submitter = serializers.CharField(source='submitter.get_full_name')
    def get_readonly(self,obj):
        return True
\
class ProposalUserActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalUserAction
        fields = '__all__'

class ProposalLogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalLogEntry
        fields = '__all__'
