import os

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from preserialize.serialize import serialize

from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.forms import IssueLicenceForm
from wildlifelicensing.apps.main.pdf import create_licence_pdf
from wildlifelicensing.apps.applications.models import Application, Assessment
from wildlifelicensing.apps.applications.utils import format_application


APPLICATION_SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class IssueLicenceView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/issue/issue_licence.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        kwargs['application'] = serialize(application, posthook=format_application)

        purposes = '\n\n'.join(Assessment.objects.filter(application=application).values_list('purpose', flat=True))

        kwargs['issue_licence_form'] = IssueLicenceForm(purpose=purposes)

        return super(IssueLicenceView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        issue_licence_form = IssueLicenceForm(request.POST)

        if issue_licence_form.is_valid():
            licence = issue_licence_form.save(commit=False)
            licence.licence_type = application.licence_type
            licence.profile = application.applicant_profile
            licence.user = application.applicant_profile.user
            licence.save()

            application.licence = licence
            application.save()

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="licence.pdf"'

            response.write(create_licence_pdf('licence.pdf', licence, application))

            return response
