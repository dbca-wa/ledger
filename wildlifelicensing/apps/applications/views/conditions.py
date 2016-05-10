import os
import json

from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View, TemplateView
from django.core.urlresolvers import reverse, reverse_lazy

from preserialize.serialize import serialize

from wildlifelicensing.apps.main.models import Condition
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin, OfficerOrAssessorRequiredMixin, AssessorRequiredMixin
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder
from wildlifelicensing.apps.applications.models import Application, ApplicationCondition, Assessment, AssessmentCondition
from wildlifelicensing.apps.applications.utils import format_application, format_assessment, ASSESSMENT_CONDITION_ACCEPTANCE_STATUSES
from wildlifelicensing.apps.applications.emails import send_assessment_done_email
from wildlifelicensing.apps.applications.views.process import determine_processing_status
from wildlifelicensing.apps.applications.mixins import CanEditAssessmentMixin
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
        kwargs['assessments'] = serialize(Assessment.objects.filter(application=application), posthook=format_assessment)
        kwargs['action_url'] = reverse('applications:submit_conditions', args=[application.pk])

        return super(EnterConditionsView, self).get_context_data(**kwargs)


class EnterConditionsAssessorView(CanEditAssessmentMixin, EnterConditionsView):
    template_name = 'wl/conditions/assessor_enter_conditions.html'

    def get_context_data(self, **kwargs):
        ctx = super(EnterConditionsAssessorView, self).get_context_data(**kwargs)
        try:
            application_pk = ctx['application']['id']
        except KeyError:
            application_pk = get_object_or_404(Application, pk=self.args[0]).pk
        assessment = get_object_or_404(Assessment, pk=self.args[1])
        ctx['assessment'] = assessment
        #  override action url
        ctx['action_url'] = reverse('applications:submit_conditions_assessor',
                                    args=[application_pk, assessment.pk])
        return ctx


class SearchConditionsView(OfficerOrAssessorRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')

        if query is not None:
            q = Q(code__icontains=query) | Q(text__icontains=query) & Q(one_off=False)
            qs = Condition.objects.filter(q)
        else:
            qs = Condition.objects.none()
        conditions = serialize(qs)

        return JsonResponse(conditions, safe=False, encoder=WildlifeLicensingJSONEncoder)


class CreateConditionView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            response = serialize(Condition.objects.create(code=request.POST.get('code'), text=request.POST.get('text'),
                                                          one_off=not request.POST.get('addToGeneralList', False)))
        except IntegrityError:
            response = 'This code has already been used. Please enter a unique code.'

        return JsonResponse(response, safe=False, encoder=WildlifeLicensingJSONEncoder)


class SetAssessmentConditionState(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        assessment_condition = get_object_or_404(AssessmentCondition, pk=request.POST.get('assessmentConditionID'))

        assessment_condition.acceptance_status = request.POST.get('acceptanceStatus')
        assessment_condition.save()

        response = ASSESSMENT_CONDITION_ACCEPTANCE_STATUSES[assessment_condition.acceptance_status]

        return JsonResponse(response, safe=False, encoder=WildlifeLicensingJSONEncoder)


class SubmitConditionsView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        application.processing_status = 'ready_to_issue'

        # remove existing conditions as there may be new conditions and/or changes of order
        application.conditions.clear()

        application.save()

        for order, condition_id in enumerate(request.POST.getlist('conditionID')):
            ApplicationCondition.objects.create(condition=Condition.objects.get(pk=condition_id),
                                                application=application, order=order)

        if request.POST.get('submissionType') == 'backToProcessing':
            return redirect('applications:process', *args)
        else:
            return redirect('applications:issue_licence', *self.args, **self.kwargs)


class SubmitConditionsAssessorView(CanEditAssessmentMixin, View):
    success_url = reverse_lazy('dashboard:home')

    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])
        assessment = get_object_or_404(Assessment, pk=self.args[1])

        for order, condition_id in enumerate(request.POST.getlist('conditionID')):
            AssessmentCondition.objects.create(condition=Condition.objects.get(pk=condition_id),
                                               assessment=assessment, order=order)

        # set the assessment request status to be 'assessed'
        assessment.status = 'assessed'
        comment = request.POST.get('comment', '')
        if len(comment.strip()) > 0:
            assessment.comment = comment
        assessment.save()

        # set application status process
        application.processing_status = determine_processing_status(application)
        application.save()

        send_assessment_done_email(assessment, request)

        return redirect(self.success_url)
