import os

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from preserialize.serialize import serialize

from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.forms import IssueLicenceForm
from wildlifelicensing.apps.main.pdf import create_licence_pdf_document
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

            filename = '%s.pdf' % application.lodgement_number

            licence.document = create_licence_pdf_document(filename, licence, application)

            licence.save()

            application.customer_status = 'approved'
            application.processing_status = 'issued'
            application.licence = licence

            application.save()

            messages.success(request, 'The licence has now been issued.')

            return redirect('dashboard:home')
        else:
            purposes = '\n\n'.join(Assessment.objects.filter(application=application).values_list('purpose', flat=True))

            return render(request, self.template_name, {'application': serialize(application, posthook=format_application),
                                                        'issue_licence_form': IssueLicenceForm(purpose=purposes)})
