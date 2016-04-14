from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import View, TemplateView

from preserialize.serialize import serialize

from wildlifelicensing.apps.main.models import Condition
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.applications.utils import format_application_statuses


class EnterConditionsView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/conditions/enter_conditions.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        kwargs['application'] = serialize(application, posthook=format_application_statuses)

        return super(EnterConditionsView, self).get_context_data(**kwargs)


class SearchConditionsView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')

        conditions = serialize(Condition.objects.filter(text__icontains=query))

        return JsonResponse(conditions, safe=False, encoder=WildlifeLicensingJSONEncoder)
