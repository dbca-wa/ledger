import os
import json

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View, TemplateView

from preserialize.serialize import serialize

from wildlifelicensing.apps.main.models import Condition
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin, OfficerOrAssessorRequiredMixin
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder
from wildlifelicensing.apps.applications.models import Application, ApplicationCondition
from wildlifelicensing.apps.applications.utils import format_application
from django.db.utils import IntegrityError

APPLICATION_SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class EnterConditionsView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/conditions/enter_conditions.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, application.licence_type.code)) as data_file:
            form_structure = json.load(data_file)

        kwargs['application'] = serialize(application, posthook=format_application)
        kwargs['form_structure'] = form_structure

        return super(EnterConditionsView, self).get_context_data(**kwargs)


class EnterConditionsAssessorView(OfficerOrAssessorRequiredMixin, EnterConditionsView):
    template_name = 'wl/conditions/assessor_enter_conditions.html'


class SearchConditionsView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')

        q = Q(code__icontains=query) | Q(text__icontains=query) & Q(one_off=False)

        conditions = serialize(Condition.objects.filter(q))

        return JsonResponse(conditions, safe=False, encoder=WildlifeLicensingJSONEncoder)


class CreateConditionView(View):
    def post(self, request, *args, **kwargs):
        try:
            response = serialize(Condition.objects.create(code=request.POST.get('code'), text=request.POST.get('text'),
                                                          one_off=not request.POST.get('addToGeneralList', False)))
        except IntegrityError:
            response = 'This code has already been used. Please enter a unique code.'

        return JsonResponse(response, safe=False, encoder=WildlifeLicensingJSONEncoder)


class SubmitConditionsView(View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        # remove existing conditions as there may be new conditions and/or changes of order
        application.conditions.clear()

        for order, condition_id in enumerate(request.POST.getlist('conditionID')):
            ApplicationCondition.objects.create(condition=Condition.objects.get(pk=condition_id),
                                                application=application, order=order)

        if request.POST.get('submissionType') == 'backToProcessing':
            return redirect('applications:process', *args)
        else:
            return redirect('dashboard:home')
