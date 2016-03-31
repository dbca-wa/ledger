import json
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404

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
