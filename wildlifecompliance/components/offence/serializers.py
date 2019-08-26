from rest_framework import serializers

from ledger.accounts.models import Organisation
from wildlifecompliance.components.call_email.serializers import LocationSerializer, EmailUserSerializer
from wildlifecompliance.components.main.fields import CustomChoiceField
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


class OffenceDatatableSerializer(serializers.ModelSerializer):
    status = CustomChoiceField(read_only=True)
    user_action = serializers.SerializerMethodField()
    alleged_offences = SectionRegulationSerializer(read_only=True, many=True)
    offenders = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Offence
        fields = (
            'id',
            'identifier',
            'status',
            'lodgement_number',
            # 'region',
            # 'district',
            # 'offence',
            'offenders',
            'alleged_offences',
            # 'issued_on_paper',
            # 'paper_id',
            'occurrence_from_to',
            'occurrence_date_from',
            'occurrence_time_from',
            'occurrence_date_to',
            'occurrence_time_to',
            'details',
            'user_action',
        )
        read_only_fields = ()

    def get_user_action(self, obj):
        user_id = self.context.get('request', {}).user.id
        view_url = '<a href=/internal/offence/' + str(obj.id) + '>View</a>'
        process_url = '<a href=/internal/offence/' + str(obj.id) + '>Process</a>'
        returned_url = ''

        if obj.status == 'closed':
            returned_url = view_url
        elif user_id == obj.assigned_to_id:
            returned_url = process_url
        elif (obj.allocated_group
              and not obj.assigned_to_id):
            for member in obj.allocated_group.members:
                if user_id == member.id:
                    returned_url = process_url

        if not returned_url:
            returned_url = view_url

        return returned_url

    def get_offenders(self, obj):
        offenders = Offender.active_offenders.filter(offence__exact=obj)
        return [ OffenderSerializer(offender).data for offender in offenders ]


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
            'inspection_id',
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
    inspection_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)

    class Meta:
        model = Offence
        fields = (
            'id',
            'identifier',
            'status',
            'location_id',
            'call_email_id',
            'inspection_id',
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
