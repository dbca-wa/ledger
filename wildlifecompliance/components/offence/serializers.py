from rest_framework import serializers
from wildlifecompliance.components.call_email.serializers import LocationSerializer
from wildlifecompliance.components.offence.models import Offence, SectionRegulation


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


class OffenceSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    alleged_offences = SectionRegulationSerializer(read_only=True, many=True)

    class Meta:
        model = Offence
        fields = (
            'id',
            'identifier',
            'status',
            'call_email',
            'occurrence_from_to',
            'occurrence_date_from',
            'occurrence_time_from',
            'occurrence_date_to',
            'occurrence_time_to',
            'details',
            'location',
            'alleged_offences',
        )
        read_only_fields = (

        )


class SaveOffenceSerializer(serializers.ModelSerializer):
    location_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    call_email_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)

    class Meta:
        model = Offence
        fields = (
            'id',
            'identifier',
            'status',
            'location_id',
            'call_email_id',
            'occurrence_from_to',
            'occurrence_date_from',
            'occurrence_time_from',
            'occurrence_date_to',
            'occurrence_time_to',
            'details',
        )
        read_only_fields = (

        )



