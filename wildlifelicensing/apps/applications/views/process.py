from django.contrib.auth.models import Group
from django.core.context_processors import csrf
from django.db.models import Q
import os
import json

from django.http import JsonResponse
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404

from preserialize.serialize import serialize

from ledger.accounts.models import EmailUser

from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.helpers import get_all_officers, get_all_assessors
from wildlifelicensing.apps.applications.models import Application,\
    AmendmentRequest

APPLICATION_SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

PROCESSING_STATUSES = dict(Application.PROCESSING_STATUS_CHOICES)
ID_CHECK_STATUSES = dict(Application.ID_CHECK_STATUS_CHOICES)
CHARACTER_CHECK_STATUSES = dict(Application.CHARACTER_CHECK_STATUS_CHOICES)
REVIEW_STATUSES = dict(Application.REVIEW_STATUS_CHOICES)


class ProcessView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/process/process_app.html'

    def _build_data(self, request, application):
        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, application.licence_type.code)) as data_file:
            form_structure = json.load(data_file)

        officers = [{'id': officer.id, 'text': officer.first_name + ' ' + officer.last_name} for officer in get_all_officers()]
        officers.insert(0, {'id': 0, 'text': 'Unassigned'})

        assessors = [{'id': assessor.id, 'text': assessor.first_name + ' ' + assessor.last_name} for assessor in get_all_assessors()]

        def format_application_statuses(instance, attrs):
            attrs['processing_status'] = PROCESSING_STATUSES[attrs['processing_status']]
            attrs['id_check_status'] = ID_CHECK_STATUSES[attrs['id_check_status']]
            attrs['character_check_status'] = CHARACTER_CHECK_STATUSES[attrs['character_check_status']]
            attrs['review_status'] = REVIEW_STATUSES[attrs['review_status']]

            return attrs

        data = {
            'user': serialize(request.user),
            'application': serialize(application, posthook=format_application_statuses),
            'form_structure': form_structure,
            'officers': officers,
            'assessors': assessors,
            'csrf_token': str(csrf(request).get('csrf_token'))
        }

        return data

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=kwargs['id'])
        if 'data' not in kwargs:
            kwargs['data'] = self._build_data(self.request, application)
        return super(ProcessView, self).get_context_data(**kwargs)


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

        return JsonResponse({'assigned_officer': assigned_officer, 'processing_status': PROCESSING_STATUSES[application.processing_status]},
                            safe=False)


class SetIDCheckStatusView(View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])
        application.id_check_status = request.POST['status']

        if 'message' in request.POST:
            print request.POST.get('message')

        application.processing_status = _determine_processing_status(application)
        application.save()

        return JsonResponse({'id_check_status': ID_CHECK_STATUSES[application.id_check_status],
                             'processing_status': PROCESSING_STATUSES[application.processing_status]}, safe=False)


class SetCharacterCheckStatusView(View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])
        application.character_check_status = request.POST['status']

        application.processing_status = _determine_processing_status(application)
        application.save()

        return JsonResponse({'character_check_status': CHARACTER_CHECK_STATUSES[application.character_check_status],
                             'processing_status': PROCESSING_STATUSES[application.processing_status]}, safe=False)


class SetReviewStatusView(View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST['applicationID'])
        application.review_status = request.POST['status']

        if application.review_status == 'awaiting_amendments':
            application.customer_status = 'amendment_required'
            AmendmentRequest.objects.create(application=application, text=request.POST.get('message', ''))

        application.processing_status = _determine_processing_status(application)
        application.save()

        return JsonResponse({'review_status': REVIEW_STATUSES[application.review_status],
                             'processing_status': PROCESSING_STATUSES[application.processing_status]}, safe=False)


def _determine_processing_status(application):
    status = application.processing_status

    if application.assigned_officer is not None:
        status = 'ready_for_action'

    if application.id_check_status == 'awaiting_update' or application.review_status == 'awaiting_amendments':
        status = 'awaiting_applicant_response'

    return status
