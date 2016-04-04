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
from wildlifelicensing.apps.applications.models import Application

APPLICATION_SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class ProcessView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/process/process_app.html'

    def _build_data(self, request, application):
        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, application.licence_type.code)) as data_file:
            form_structure = json.load(data_file)

        def format_application_statuses(instance, attrs):
            attrs['processing_status'] = dict(Application.PROCESSING_STATUS_CHOICES)[attrs['processing_status']]
            return attrs

        data = {
                'user': serialize(request.user),
                'application': serialize(application, posthook=format_application_statuses),
                'form_structure': form_structure,
                'csrf_token': str(csrf(request).get('csrf_token'))
                }

        return data

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=kwargs['id'])
        if 'dataJSON' not in kwargs:
            kwargs['dataJSON'] = self._build_data(self.request, application)
        return super(ProcessView, self).get_context_data(**kwargs)


class ListOfficersView(View):
    def get(self, request, *args, **kwargs):
        if 'name' in request.GET and len(request.GET.get('name')) > 0:
            q = Q(last_name__istartswith=request.GET.get('name')) | Q(first_name__istartswith=request.GET.get('name'))

            q = q & Q(groups=get_object_or_404(Group, name='Officers'))

            officer_email_users = EmailUser.objects.filter(q)
            officers = []
        else:
            officers = [{'id': 0, 'text': 'Unassigned'}]
            officer_email_users = EmailUser.objects.filter(groups=get_object_or_404(Group, name='Officers'))

        for user in officer_email_users:
            officers.append({'id': user.id, 'text': '%s %s' % (user.first_name, user.last_name)})

        return JsonResponse(officers, safe=False)


class AssignOfficerView(View):
    def post(self, request, *args, **kwargs):

        application = get_object_or_404(Application, pk=request.POST['applicationID'])

        try:
            application.assigned_officer = EmailUser.objects.get(pk=request.POST['userID'])
        except EmailUser.DoesNotExist:
            application.assigned_officer = None

        application.save()

        if application.assigned_officer is not None:
            return JsonResponse({'id': application.assigned_officer.id, 'text': '%s %s' % \
                                 (application.assigned_officer.first_name, application.assigned_officer.last_name)}, safe=False)
        else:
            return JsonResponse({'id': 0, 'text': 'Unassigned'})
