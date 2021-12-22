from django.conf import settings
from rest_framework import serializers
import rest_framework_gis.serializers as gis_serializers

class ReportSerializer(serializers.Serializer):
    start = serializers.DateTimeField(input_formats=['%d/%m/%Y'])
    end = serializers.DateTimeField(input_formats=['%d/%m/%Y'])

class SettlementReportSerializer(serializers.Serializer):
    date = serializers.DateTimeField(input_formats=['%d/%m/%Y'])

class OracleSerializer(serializers.Serializer):
    date = serializers.DateField(input_formats=['%d/%m/%Y','%Y-%m-%d'])
    override = serializers.BooleanField(default=False)

