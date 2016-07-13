from django.http import HttpResponse
from django.views.generic import View
import json

from .models import Species


class SpeciesNamesJSON(View):
    def get(self, request):
        """Returns JSON of all species names.
        """
        names = [sp.species_name for sp in Species.objects.all()]
        return HttpResponse(json.dumps(names), content_type='application/json')
