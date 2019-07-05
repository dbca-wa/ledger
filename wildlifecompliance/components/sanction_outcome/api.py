import json
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.decorators import list_route

from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome
from wildlifecompliance.components.sanction_outcome.serializers import SanctionOutcomeSerializer
from wildlifecompliance.helpers import is_internal


class SanctionOutcomeViewSet(viewsets.ModelViewSet):
    queryset = SanctionOutcome.objects.all()
    serializer_class = SanctionOutcomeSerializer

    def get_queryset(self):
        user = self.request.user
        if is_internal(self.request):
            return SanctionOutcome.objects.all()
        return SanctionOutcome.objects.none()

    @list_route(methods=['GET', ])
    def types(self, request, *args, **kwargs):
        res_obj = []
        for choice in SanctionOutcome.TYPE_CHOICES:
            res_obj.append({'id': choice[0], 'display': choice[1]});
        res_json = json.dumps(res_obj)
        return HttpResponse(res_json, content_type='application/json')
