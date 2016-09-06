import csv
from collections import OrderedDict

from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View

from wildlifelicensing.apps.returns.models import ReturnType, ReturnRow
from wildlifelicensing.apps.returns.utils_schema import Schema


class ExplorerView(View):
    """
    Return a JSOn representation of the ReturnTypes.
    The main goal of this view is to provide for every resources (ReturnTable) a link to download the data
    (@see ReturnsDataView view)
    """

    def get(self, request):
        queryset = ReturnType.objects.all()
        results = []
        for rt in queryset:
            return_obj = OrderedDict({'id': rt.id})
            licence_type = {
                'display_name': rt.licence_type.display_name,
                'code': rt.licence_type.code
            }
            return_obj['license_type'] = licence_type
            # resources
            resources = []
            for idx, resource in enumerate(rt.resources):
                resource_obj = OrderedDict()
                resource_obj['name'] = resource.get('name', '')
                resource_obj['data'] = request.build_absolute_uri(reverse('wl_returns:api:data', kwargs={
                    'return_type_pk': rt.pk,
                    'resource_number': idx
                }))
                resource_obj['schema'] = resource.get('schema', {})
                resources.append(resource_obj)

            return_obj['resources'] = resources
            results.append(return_obj)

        return JsonResponse(results, safe=False)


class ReturnsDataView(View):
    """
    Export returns data in CSV format.
    """

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
