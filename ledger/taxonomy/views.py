import json
import requests

from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings


def add_filter(cql_filter, params):
    if 'cql_filter' not in params:
        params['cql_filter'] = cql_filter
    else:
        params['cql_filter'] = params['cql_filter'] + ' AND ' + cql_filter


class SpeciesNamesJSON(View):

    def get(self, request, *args, **kwargs):
        base_url = settings.HERBIE_SPECIES_WFS_URL
        params = {'propertyName': 'species_name', 'sortBy': 'species_name'}
        # search filter. The search is equivalent to a 'icontains' query.
        search = request.GET.get('search')
        if search:
            filter_ = "species_name ILIKE '%{}%'".format(search)
            add_filter(filter_, params)
        kingdom = request.GET.get('type')
        if kingdom == 'fauna':
            add_filter('kingdom_id in (5)', params)
        elif kingdom == 'flora':
            add_filter('kingdom_id in (3)', params)
        r = requests.get(base_url, params=params)
        names = []
        if r.status_code == 200:
            features = r.json()['features']
            names = [f['properties']['species_name'] for f in features]
        return HttpResponse(json.dumps(names), content_type='application/json')
