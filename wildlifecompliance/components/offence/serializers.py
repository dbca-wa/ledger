from rest_framework import serializers

from ledger.accounts.models import Organisation
from wildlifecompliance.components.call_email.serializers import LocationSerializer, EmailUserSerializer
from wildlifecompliance.components.offence.models import Offence, SectionRegulation, Offender


class OrganisationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organisation
        fields = (
            'id',
            'abn',
            'name',
        )
        read_only_fields = ()


class SectionRegulationSerializer(serializers.ModelSerializer):

    class Meta:
        model = SectionRegulation
        fields = (
            'id',
            'act',
            'name',
            'offence_text',
        )
        read_only_fields = ()


class OffenderSerializer(serializers.ModelSerializer):
    person = EmailUserSerializer(read_only=True,)
    organisation = OrganisationSerializer(read_only=True,)

    class Meta:
        model = Offender
        fields = (
            'id',
            'person',
            'organisation',
        )


class OffenceSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    alleged_offences = SectionRegulationSerializer(read_only=True, many=True)
    offenders = serializers.SerializerMethodField(read_only=True)

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
            'offenders',
        )
        read_only_fields = (

        )

    def get_offenders(self, obj):
        offenders = Offender.active_offenders.filter(offence__exact=obj)
        return [ OffenderSerializer(offender).data for offender in offenders ]

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
        read_only_fields = ()


class SaveOffenderSerializer(serializers.ModelSerializer):
    offence_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    person_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    organisation_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)

    class Meta:
        model = Offender
        fields = (
            'id',
            'offence_id',
            'person_id',
            'organisation_id',
        )
        read_only_fields = ()
