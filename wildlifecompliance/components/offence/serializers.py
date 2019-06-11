from rest_framework import serializers
from wildlifecompliance.components.offence.models import Offence


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
            'description',
        )
        read_only_fields = (

        )
