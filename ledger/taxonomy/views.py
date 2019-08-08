import json
import requests
import logging

from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings

logger = logging.getLogger('log')


def add_filter(cql_filter, params):
    if 'cql_filter' not in params:
        params['cql_filter'] = cql_filter
    else:
        params['cql_filter'] = params['cql_filter'] + ' AND ' + cql_filter


class SpeciesNamesJSON(View):
    def get(self, request, *args, **kwargs):
        """
        Search herbie for species and return a list of matching species in the form 'scientific name (common name)'.
        The 'search' parameter is used to search (icontains like) through the species_name (scientific name)
        and vernacular property (common name).
        The 'type'=['fauna'|'flora'] parameter can be used to limit the kingdom.

        :return: a list of matching species in the form 'scientific name (common name)'
        """
        base_url = settings.HERBIE_SPECIES_WFS_URL
        params = {'propertyName': '(species_name,vernacular)', 'sortBy': 'species_name'}
        search = request.GET.get('search')
        if search:
            filter_ = "(species_name ILIKE '%{1}%' OR vernacular ILIKE '%{1}%')".format(search, search)
            add_filter(filter_, params)
        kingdom = request.GET.get('type')
        fauna_kingdom = 5
        if kingdom == 'fauna':
            add_filter('kingdom_id IN ({})'.format(fauna_kingdom), params)
        elif kingdom == 'flora':
            add_filter('kingdom_id NOT IN ({})'.format(fauna_kingdom), params)
        r = requests.get(base_url, params=params, verify=False)
        names = []
        try:
            features = r.json()['features']
            for f in features:
                name = f['properties']['species_name']
                common_name = f['properties']['vernacular'] if 'vernacular' in f['properties'] else None
                if common_name:
                    name += ' ({})'.format(common_name)
                names.append(name)
        except Exception as e:
            logger.warning('Herbie returned an error: {}. \nURL: {}. \nResponse: {}'.format(e, r.url, r.content))
        return HttpResponse(json.dumps(names), content_type='application/json')
