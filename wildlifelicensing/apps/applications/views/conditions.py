from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
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

        q = Q(code__icontains=query) | Q(text__icontains=query)

        conditions = serialize(Condition.objects.filter(q))

        return JsonResponse(conditions, safe=False, encoder=WildlifeLicensingJSONEncoder)


class CreateConditionView(View):
    def post(self, request, *args, **kwargs):
        condition = Condition.objects.create(code=request.POST.get('code'), text=request.POST.get('text'), one_off=True)

        return JsonResponse(serialize(condition), safe=False, encoder=WildlifeLicensingJSONEncoder)


class SubmitConditionsView(View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        for condition_id in request.POST.getlist('conditionID'):
            if int(condition_id) not in application.conditions.all().values_list('id', flat=True):
                application.conditions.add(condition_id)

        if 'backToProcessing' in request.POST:
            return redirect('applications:process', *args)
        else:
            return redirect('dashboard:home')
