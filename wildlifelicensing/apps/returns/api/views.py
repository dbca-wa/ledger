import csv

from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from rest_framework.generics import ListAPIView
from rest_framework.renderers import JSONRenderer

from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.returns.models import ReturnType, ReturnTable, ReturnRow
from wildlifelicensing.apps.returns.utils_schema import Schema
from wildlifelicensing.apps.returns.api.serializers import ReturnTypeSerializer


class ReturnListView(OfficerRequiredMixin, ListAPIView):
    queryset = ReturnType.objects.all()
    renderer_classes = (JSONRenderer,)
    serializer_class = ReturnTypeSerializer


class ReturnsData(OfficerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return_type = get_object_or_404(ReturnType, pk=kwargs.get('return_type_pk'))
        resource_number = kwargs.get('resource_number')
        if not resource_number:
            resource_number = 0
        else:
            resource_number = int(resource_number)
        all_resources = return_type.resources
        if resource_number >= len(all_resources):
            raise Http404("Invalid resource number {}. The Return Type {} has only {} resources".format(
                resource_number, return_type.licence_type, len(all_resources))
            )

        resource_name = return_type.get_resources_names()[resource_number]
        qs = ReturnRow.objects.filter(return_table__name=resource_name)
        schema = Schema(return_type.get_schema_by_name(resource_name))
        response = HttpResponse(content_type='text/csv')
        file_name = 'wl_returns_{}.csv'.format(resource_name)
        response['Content-Disposition'] = 'attachment; filename={}'.format(file_name)
        writer = csv.writer(response)
        writer.writerow(schema.headers)
        for ret_row in qs:
            row = []
            for field in schema.field_names:
                row.append(unicode(ret_row.data.get(field, '')))
            writer.writerow(row)
        return response
