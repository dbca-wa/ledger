import json
import requests

from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings


class SpeciesNamesJSON(View):
    def get(self, request, *args, **kwargs):
        base_url = settings.HERBIE_SPECIES_WFS_URL
        params = {'sortBy': 'species_name'}
        # search filter. The search is equivalent to a 'icontains' query.
        search = request.GET.get('search')
        if search:
            params['cql_filter'] = "species_name ILIKE '%{}%'".format(search)
        r = requests.get(base_url, params=params)
        names = []
        if r.status_code == 200:
            features = r.json()['features']
            names = [f['properties']['species_name'] for f in features]
        return HttpResponse(json.dumps(names), content_type='application/json')
