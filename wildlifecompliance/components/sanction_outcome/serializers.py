from rest_framework import serializers
from rest_framework_datatables.pagination import DatatablesPageNumberPagination

from wildlifecompliance.components.main.fields import CustomChoiceField
from wildlifecompliance.components.offence.serializers import SectionRegulationSerializer, OffenderSerializer, \
    OffenceSerializer
from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome, RemediationAction


class SanctionOutcomeSerializer(serializers.ModelSerializer):
    status = CustomChoiceField(read_only=True)
    type = CustomChoiceField(read_only=True)
    alleged_offences = SectionRegulationSerializer(read_only=True, many=True)
    offender = OffenderSerializer(read_only=True,)
    offence = OffenceSerializer(read_only=True,)

    class Meta:
        model = SanctionOutcome
        fields = (
            'id',
            'type',
            'status',
            'lodgement_number',
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


class SanctionOutcomeDatatableSerializer(serializers.ModelSerializer):
    status = CustomChoiceField(read_only=True)
    user_action = serializers.SerializerMethodField()
    offender = OffenderSerializer(read_only=True,)

    class Meta:
        model = SanctionOutcome
        fields = (
            'id',
            'type',
            'status',
            'lodgement_number',
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
            'user_action',
        )
        read_only_fields = ()

    def get_user_action(self, obj):
        user_id = self.context.get('request', {}).user.id
        view_url = '<a href=/internal/sanction_outcome/' + str(obj.id) + '>View</a>'
        process_url = '<a href=/internal/sanction_outcome/' + str(obj.id) + '>Process</a>'
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


class SaveSanctionOutcomeSerializer(serializers.ModelSerializer):
    offence_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    offender_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    region_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    district_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)
    allocated_group_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)

    class Meta:
        model = SanctionOutcome
        fields = (
            'id',
            'type',
            'identifier',
            'offence_id',
            'offender_id',
            'region_id',
            'district_id',
            'allocated_group_id',
            # 'alleged_offences',
            'issued_on_paper',
            'paper_id',
            'description',
            'date_of_issue',
            'time_of_issue',
        )


class SaveRemediationActionSerializer(serializers.ModelSerializer):
    sanction_outcome_id = serializers.IntegerField(required=False, write_only=True, allow_null=True)

    class Meta:
        model = RemediationAction
        fields = (
            'id',
            'action',
            'due_date',
            'sanction_outcome_id',
        )
