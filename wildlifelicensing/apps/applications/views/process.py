import json
from django.db.models import Q
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404

from ledger.accounts.models import EmailUser

from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.helpers import get_all_officers
from wildlifelicensing.apps.applications.models import Application


class ProcessView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/process/process_app.html'

    def _build_data(self, application):
        data = {
            'selectAssignee': {
                'values': [['', 'Unassigned']],
                'selected': ''
            }
        }
        officers = get_all_officers()
        data['selectAssignee']['values'] += [[user.email, str(user)] for user in officers]
        if application.assigned_officer is not None:
            assignee = application.assigned_officer.email
        else:
            assignee = ''
        data['selectAssignee']['selected'] = assignee
        return data

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=kwargs['id'])
        if 'dataJSON' not in kwargs:
            kwargs['dataJSON'] = json.dumps(self._build_data(application))
        return super(ProcessView, self).get_context_data(**kwargs)


class ListStaffView(View):
    def get(self, request, *args, **kwargs):
        if len(args) > 0:
            staff_email_users = EmailUser.objects.filter(id=args[0])
        else:
            q = Q(last_name__istartswith=request.GET.get('name', '')) | \
                Q(first_name__istartswith=request.GET.get('name', '')) | \
                Q(email__istartswith=request.GET.get('name', ''))

            staff_email_users = EmailUser.objects.filter(q).exclude(groups=None)

        staff = [{'id': 0, 'text': 'Unassigned'}]
        for user in staff_email_users:
            staff.append({'id': user.id, 'text': '%s %s (%s)' % (user.first_name, user.last_name, user.email)})

        return JsonResponse(staff, safe=False)


class AssignStaffView(View):
    def post(self, request, *args, **kwargs):
        get_object_or_404(Application, pk=args[0]).assigned_officer = get_object_or_404(EmailUser, pk=args[1])

        return HttpResponse('')
