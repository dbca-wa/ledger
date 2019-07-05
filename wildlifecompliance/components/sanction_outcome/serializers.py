from rest_framework import serializers

from wildlifecompliance.components.offence.serializers import SectionRegulationSerializer
from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome


class SanctionOutcomeSerializer(serializers.ModelSerializer):
    alleged_offences = SectionRegulationSerializer(read_only=True, many=True)

    class Meta:
        model = SanctionOutcome
        fields = (
            'id',
            'type',
            'region',
            'district',
            'identifier',
            'offence',
            'offender',
            'alleged_offences',
            'issued_on_paper',
            'paper_id',
            'description',
            'date_of_issue',
            'time_of_issue',
        )
        read_only_fields = ()


class SaveSanctionOutcomeSerializer(serializers.ModelSerializer):
    offence_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    offender_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)

    class Meta:
        model = SanctionOutcome
        fields = (
            'id',
            'type',
            # 'region',
            # 'district',
            'identifier',
            'offence_id',
            'offender_id',
            # 'alleged_offences',
            'issued_on_paper',
            'paper_id',
            'description',
            'date_of_issue',
            'time_of_issue',
        )
