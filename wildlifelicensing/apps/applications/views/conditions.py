from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View, TemplateView
from django.core.urlresolvers import reverse, reverse_lazy

from preserialize.serialize import serialize

from wildlifelicensing.apps.main.models import Condition
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin, OfficerOrAssessorRequiredMixin
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder
from wildlifelicensing.apps.main.forms import CommunicationsLogEntryForm
from wildlifelicensing.apps.applications.models import Application, ApplicationCondition, Assessment, AssessmentCondition
from wildlifelicensing.apps.applications.utils import convert_documents_to_url, format_application, \
    format_assessment, ASSESSMENT_CONDITION_ACCEPTANCE_STATUSES
from wildlifelicensing.apps.applications.emails import send_assessment_done_email
from wildlifelicensing.apps.applications.views.process import determine_processing_status
from wildlifelicensing.apps.applications.mixins import CanPerformAssessmentMixin


class EnterConditionsView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/conditions/enter_conditions.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        convert_documents_to_url(application.licence_type.application_schema,
                                              application.data, application.documents.all())

        kwargs['application'] = serialize(application, posthook=format_application)
        kwargs['form_structure'] = application.licence_type.application_schema
        kwargs['assessments'] = serialize(Assessment.objects.filter(application=application), posthook=format_assessment)
        kwargs['action_url'] = reverse('wl_applications:submit_conditions', args=[application.pk])

        if application.proxy_applicant is None:
            to = application.applicant_profile.user.email
        else:
            to = application.proxy_applicant.email

        kwargs['log_entry_form'] = CommunicationsLogEntryForm(to=to, fromm=self.request.user.email)

        return super(EnterConditionsView, self).get_context_data(**kwargs)


class EnterConditionsAssessorView(CanPerformAssessmentMixin, TemplateView):
    template_name = 'wl/conditions/assessor_enter_conditions.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        convert_documents_to_url(application.licence_type.application_schema, application.data, application.documents.all())

        kwargs['application'] = serialize(application, posthook=format_application)
        kwargs['form_structure'] = application.licence_type.application_schema

        assessment = get_object_or_404(Assessment, pk=self.args[1])

        kwargs['assessment'] = assessment
        kwargs['action_url'] = reverse('wl_applications:submit_conditions_assessor', args=[application.pk, assessment.pk])

        return super(EnterConditionsAssessorView, self).get_context_data(**kwargs)


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
            return redirect('wl_applications:process', *args)
        else:
            return redirect('wl_applications:issue_licence', *self.args, **self.kwargs)


class SubmitConditionsAssessorView(CanPerformAssessmentMixin, View):
    success_url = reverse_lazy('wl_dashboard:home')

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

        purpose = request.POST.get('purpose', '')
        if len(purpose.strip()) > 0:
            assessment.purpose = purpose

        assessment.save()

        # set application status process
        application.processing_status = determine_processing_status(application)
        application.save()

        send_assessment_done_email(assessment, request)

        return redirect(self.success_url)
