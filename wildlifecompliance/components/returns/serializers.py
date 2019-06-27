from ledger.accounts.models import EmailUser
from wildlifecompliance.components.applications.models import ReturnRequest
from wildlifecompliance.components.main.fields import CustomChoiceField
from wildlifecompliance.components.returns.models import (
    Return,
    ReturnType,
    ReturnUserAction,
    ReturnLogEntry,
)
from rest_framework import serializers


class EmailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUser
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'title',
            'organisation')


class ReturnSerializer(serializers.ModelSerializer):
    # activity = serializers.CharField(source='application.activity')
    processing_status = serializers.CharField(
        source='get_processing_status_display')  # TODO: check if this should be changed to use CustomChoice
    submitter = EmailUserSerializer()
    lodgement_number = serializers.SerializerMethodField()
    sheet_activity_list = serializers.SerializerMethodField()
    sheet_species_list = serializers.SerializerMethodField()
    sheet_species = serializers.SerializerMethodField()
    licence = serializers.SerializerMethodField()

    class Meta:
        model = Return
        fields = (
            'id',
            'application',
            'due_date',
            'processing_status',
            'submitter',
            'assigned_to',
            'lodgement_number',
            'lodgement_date',
            'nil_return',
            'licence',
            'resources',
            'table',
            'condition',
            'format',
            'template',
            'has_payment',
            'sheet_activity_list',
            'sheet_species_list',
            'sheet_species',
            'return_fee',
        )

    def get_lodgement_number(self, _return):
        """
        Gets the lodgement number for a submitted Return.
        :param _return: Return instance.
        :return: lodgement number.
        """
        return _return.lodgement_number

    def get_sheet_activity_list(self, _return):
        """
        Gets the list of Activities available for a Return Running Sheet.
        :param _return: Return instance.
        :return: List of available activities.
        """
        return _return.sheet.activity_list if _return.has_sheet else None

    def get_sheet_species_list(self, _return):
        """
        Gets the list of Species available for a Return Running Sheet.
        :param _return: Return instance.
        :return: List of species for a Return Running Sheet.
        """
        return _return.sheet.species_list if _return.has_sheet else None

    def get_sheet_species(self, _return):
        """
        Gets the Species available for a Return Running Sheet.
        :param _return: Return instance.
        :return: species identifier for a Return Running Sheet.
        """
        return _return.sheet.species if _return.has_sheet else None

    def get_licence(self, _return):
        """
        Gets the formatted Licence Number from the return.
        :param _return: Return instance.
        :return: formatted Licence Number.
        """
        return _return.licence.licence_number


class ReturnTypeSerializer(serializers.ModelSerializer):
    data_format = CustomChoiceField(read_only=True)
    name = serializers.SerializerMethodField()

    class Meta:
        model = ReturnType
        fields = (
            'id',
            'resources',
            'data_format',
            'name',
        )

    def get_name(self, _return_type):
        """
        Present name with versioning.
        :param _return_type: Return_Type instance.
        :return: formatted name.
        """
        return '{0} - v{1}'.format(_return_type.name, _return_type.version)


class ReturnActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')

    class Meta:
        model = ReturnUserAction
        fields = '__all__'


class ReturnLogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnLogEntry
        fields = '__all__'


class ReturnRequestSerializer(serializers.ModelSerializer):
    reason = CustomChoiceField()

    class Meta:
        model = ReturnRequest
        fields = '__all__'
