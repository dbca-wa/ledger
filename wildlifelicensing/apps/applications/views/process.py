from django.core.context_processors import csrf
import os
import json

from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, redirect
from django.utils import formats

from reversion import revisions
from preserialize.serialize import serialize

from ledger.accounts.models import EmailUser

from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.helpers import get_all_officers, render_user_name
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder
from wildlifelicensing.apps.applications.models import Application, AmendmentRequest, AssessmentRequest
from wildlifelicensing.apps.applications.emails import send_amendment_requested_email, send_assessment_requested_email
from wildlifelicensing.apps.main.models import AssessorDepartment

from wildlifelicensing.apps.applications.utils import PROCESSING_STATUSES, ID_CHECK_STATUSES, CHARACTER_CHECK_STATUSES, \
    REVIEW_STATUSES, format_application, format_assessment_status

APPLICATION_SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class ProcessView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/process/process_app.html'

    def _build_data(self, request, application):
        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, application.licence_type.code)) as data_file:
            form_structure = json.load(data_file)

        officers = [{'id': officer.id, 'text': render_user_name(officer)} for officer in get_all_officers()]
        officers.insert(0, {'id': 0, 'text': 'Unassigned'})

        current_ass_depts = [ass_request.assessor_department for ass_request in AssessmentRequest.objects.filter(application=application)]
        ass_depts = [{'id': ass_dept.id, 'text': ass_dept.name} for ass_dept in
                     AssessorDepartment.objects.all().exclude(id__in=[ass_dept.pk for ass_dept in current_ass_depts])]

        previous_application_data = []
        for revision in revisions.get_for_object(application).filter(revision__comment='Details Modified').order_by('-revision__date_created'):
            previous_application_data.append({'lodgement_number': revision.object_version.object.lodgement_number +
                                              '-' + str(revision.object_version.object.lodgement_sequence),
                                              'date': formats.date_format(revision.revision.date_created, 'd/m/Y', True),
                                              'data': revision.object_version.object.data})

        data = {
            'user': serialize(request.user),
            'application': serialize(application, posthook=format_application),
            'form_structure': form_structure,
            'officers': officers,
            'amendment_requests': serialize(AmendmentRequest.objects.filter(application=application)),
            'assessor_departments': ass_depts,
            'assessments': serialize(AssessmentRequest.objects.filter(application=application),
                                     posthook=format_assessment_status),
            'previous_application_data': serialize(previous_application_data),
            'csrf_token': str(csrf(request).get('csrf_token'))
        }

        return data

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])
        if 'data' not in kwargs:
            kwargs['data'] = self._build_data(self.request, application)
        return super(ProcessView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])
        application.processing_status = 'approved'
        application.save()

        return redirect('applications:enter_conditions', *args, **kwargs)


class AssignOfficerView(View):
    def post(self, request, *args, **kwargs):

        application = get_object_or_404(Application, pk=request.POST['applicationID'])

        try:
            application.assigned_officer = EmailUser.objects.get(pk=request.POST['userID'])
        except EmailUser.DoesNotExist:
            application.assigned_officer = None

        application.processing_status = _determine_processing_status(application)
        application.save()

        if application.assigned_officer is not None:
            assigned_officer = {'id': application.assigned_officer.id, 'text': '%s %s' %
                                (application.assigned_officer.first_name, application.assigned_officer.last_name)}
        else:
            assigned_officer = {'id': 0, 'text': 'Unassigned'}

        return JsonResponse({'assigned_officer': assigned_officer,
                             'processing_status': PROCESSING_STATUSES[application.processing_status]},
                            safe=False, encoder=WildlifeLicensingJSONEncoder)


class SetIDCheckStatusView(View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])
        application.id_check_status = request.POST['status']

        if 'message' in request.POST:
            print(request.POST.get('message'))

        application.processing_status = _determine_processing_status(application)
        application.save()

        return JsonResponse({'id_check_status': ID_CHECK_STATUSES[application.id_check_status],
                             'processing_status': PROCESSING_STATUSES[application.processing_status]},
                            safe=False, encoder=WildlifeLicensingJSONEncoder)


class SetCharacterCheckStatusView(View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])
        application.character_check_status = request.POST['status']

        application.processing_status = _determine_processing_status(application)
        application.save()

        return JsonResponse({'character_check_status': CHARACTER_CHECK_STATUSES[application.character_check_status],
                             'processing_status': PROCESSING_STATUSES[application.processing_status]},
                            safe=False, encoder=WildlifeLicensingJSONEncoder)


class SetReviewStatusView(View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])
        application.review_status = request.POST['status']

        amendment_request = None
        if application.review_status == 'awaiting_amendments':
            application.customer_status = 'amendment_required'
            amendment_text = request.POST.get('message', '')
            amendment_request = AmendmentRequest.objects.create(application=application,
                                                                text=amendment_text,
                                                                user=request.user)
        application.processing_status = _determine_processing_status(application)
        application.save()
        if amendment_request is not None:
            send_amendment_requested_email(application, amendment_request, request=request)

        response = {'review_status': REVIEW_STATUSES[application.review_status],
                    'processing_status': PROCESSING_STATUSES[application.processing_status]}

        if amendment_request is not None:
            response['amendment_request'] = serialize(amendment_request)

        return JsonResponse(response, safe=False, encoder=WildlifeLicensingJSONEncoder)


class SendForAssessmentView(View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])

        ass_dept = get_object_or_404(AssessorDepartment, pk=request.POST['assDeptID'])
        assessment_request = AssessmentRequest.objects.create(application=application, assessor_department=ass_dept,
                                                              status=request.POST['status'],
                                                              user=request.user)

        application.processing_status = _determine_processing_status(application)
        application.save()
        send_assessment_requested_email(application, assessment_request, request)

        return JsonResponse({'assessment': serialize(assessment_request, posthook=format_assessment_status),
                             'processing_status': PROCESSING_STATUSES[application.processing_status]},
                            safe=False, encoder=WildlifeLicensingJSONEncoder)


def _determine_processing_status(application):
    status = 'ready_for_action'

    if application.id_check_status == 'awaiting_update' or application.review_status == 'awaiting_amendments':
        status = 'awaiting_applicant_response'

    if AssessmentRequest.objects.filter(application=application).filter(status='awaiting_assessment').exists():
        if status == 'awaiting_applicant_response':
            status = 'awaiting_responses'
        else:
            status = 'awaiting_assessor_response'

    return status
