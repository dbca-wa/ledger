import json
import os

from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404

from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.applications.mixins import UserCanViewApplicationMixin
from wildlifelicensing.apps.main.helpers import is_officer

APPLICATION_SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class ViewReadonlyView(UserCanViewApplicationMixin, TemplateView):
    template_name = 'wl/view/view_readonly.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, application.licence_type.code)) as data_file:
            form_structure = json.load(data_file)

        kwargs['licence_type'] = application.licence_type
        kwargs['structure'] = form_structure
        kwargs['data'] = application.data

        if is_officer(self.request.user):
            kwargs['customer'] = application.applicant_profile.user

        return super(ViewReadonlyView, self).get_context_data(**kwargs)
