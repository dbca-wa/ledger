from ledger.accounts.models import EmailUser
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
        source='get_processing_status_display')
    submitter = EmailUserSerializer()
    table = serializers.SerializerMethodField()
    licence_species_list = serializers.SerializerMethodField()
    sheet_activity_list = serializers.SerializerMethodField()
    sheet_species_list = serializers.SerializerMethodField()
    sheet_species = serializers.SerializerMethodField()

    class Meta:
        model = Return
        fields = (
            'id',
            'application',
            'due_date',
            'processing_status',
            'submitter',
            'assigned_to',
            'lodgement_date',
            'nil_return',
            'licence',
            'resources',
            'table',
            'condition',
            'text',
            'type',
            'licence_species_list',
            'sheet_activity_list',
            'sheet_species_list',
            'sheet_species'
        )

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

    def get_table(self, _return):
        """
        Gets the table of data available for the Return.
        :param _return: Return instance.
        :return: table of data details.
        """
        return _return.sheet.table if _return.has_sheet else _return.table

    def get_licence_species_list(self, _return):
        """
        Gets Species applicable for a Return Licence.
        :param _return: Return instance.
        :return: species identifiers for a Return Licence.
        """
        return _return.sheet.licence_species_list if _return.has_sheet else None


class ReturnTypeSerializer(serializers.ModelSerializer):
    return_type = CustomChoiceField(read_only=True)

    class Meta:
        model = ReturnType
        fields = (
            'id',
            'resources',
            'return_type',
        )


class ReturnActionSerializer(serializers.ModelSerializer):
    who = serializers.CharField(source='who.get_full_name')

    class Meta:
        model = ReturnUserAction
        fields = '__all__'


class ReturnCommsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnLogEntry
        fields = '__all__'
