from rest_framework import serializers
from wildlifecompliance.components.offence.models import Offence, SectionRegulation


class OffenceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offence
        fields = (
            'id',
            'identifier',
            'status',
            'location',
            'call_email',
            'occurrence_from_to',
            'occurrence_date_from',
            'occurrence_time_from',
            'occurrence_date_to',
            'occurrence_time_to',
            'alleged_offences',
            'details',
        )
        read_only_fields = (

        )


class SectionRegulationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SectionRegulation
        fields = (
            'id',
            'act',
            'name',
            'offence_text',
        )
        read_only_fields = (

        )
