import os

from django.contrib import messages
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView

from preserialize.serialize import serialize

from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.forms import IssueLicenceForm
from wildlifelicensing.apps.main.pdf import create_licence_pdf_document, create_licence_pdf_bytes
from wildlifelicensing.apps.applications.models import Application, Assessment
from wildlifelicensing.apps.applications.utils import format_application
from wildlifelicensing.apps.applications.emails import send_licence_issued_email


APPLICATION_SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class IssueLicenceView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/issue/issue_licence.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        kwargs['application'] = serialize(application, posthook=format_application)

        purposes = '\n\n'.join(Assessment.objects.filter(application=application).values_list('purpose', flat=True))

        kwargs['issue_licence_form'] = IssueLicenceForm(purpose=purposes, is_renewable=application.licence_type.is_renewable)

        return super(IssueLicenceView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        if application.licence is not None:
            issue_licence_form = IssueLicenceForm(request.POST, instance=application.licence)
        else:
            issue_licence_form = IssueLicenceForm(request.POST)

        if issue_licence_form.is_valid():
            licence = issue_licence_form.save(commit=False)
            licence.licence_type = application.licence_type
            licence.profile = application.applicant_profile
            licence.user = application.applicant_profile.user

            filename = '%s.pdf' % application.lodgement_number

            if not licence.licence_no:
                licence.save(no_revision=True)
                licence.licence_no = str(licence.id).zfill(9)

            licence.document = create_licence_pdf_document(filename, licence, application)

            licence.save()

            application.customer_status = 'approved'
            application.processing_status = 'issued'
            application.licence = licence

            application.save()

            # The licence should be emailed to the customer if they applied for it online. If an officer entered
            # the application on their behalf, the licence needs to be posted to the user, although if they provided
            # an email address in their offline application, they should receive the licence both via email and in the
            # post
            if application.proxy_applicant is None:
                # customer applied online
                messages.success(request, 'The licence has now been issued and sent as an email attachment to the '
                                 'licencee.')
                send_licence_issued_email(licence, application, issue_licence_form.cleaned_data['cover_letter_message'],
                                          request)
            elif not application.applicant_profile.user.email.endswith('ledger.dpaw.wa.gov.au'):
                # customer applied offline but provided an email address
                messages.success(request, 'The licence has now been issued and sent as an email attachment to the '
                                 'licencee. However, as the application was entered on behalf of the licencee by '
                                 'staff, it should also be posted to the licencee. Click the following link to show '
                                 'the licence: <a href="{0}" target="_blank">Licence PDF</a><img height="20px" '
                                 'src="{1}"></img>'.format(licence.document.file.url, static('wl/img/pdf.png')))
                send_licence_issued_email(licence, application, issue_licence_form.cleaned_data['cover_letter_message'],
                                          request)
            else:
                # customer applied offline and did not provide an email address
                messages.success(request, 'The licence has now been issued and must be posted to the licencee. Click '
                                 'the following link to show the licence: <a href="{0}" target="_blank">Licence PDF'
                                 '</a><img height="20px" src="{1}"></img>'.format(licence.document.file.url,
                                                                                  static('wl/img/pdf.png')))

            return redirect('dashboard:home')
        else:
            messages.error(request, issue_licence_form.errors)

            purposes = '\n\n'.join(Assessment.objects.filter(application=application).values_list('purpose', flat=True))

            return render(request, self.template_name, {'application': serialize(application, posthook=format_application),
                                                        'issue_licence_form': IssueLicenceForm(purpose=purposes)})


class ReissueLicenceView(OfficerRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        licence = get_object_or_404(WildlifeLicence, pk=self.args[0])

        application = get_object_or_404(Application, licence=licence)

        return redirect('applications:issue_licence', application.pk)


class PreviewLicenceView(OfficerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        issue_licence_form = IssueLicenceForm(request.GET)

        licence = issue_licence_form.save(commit=False)
        licence.licence_type = application.licence_type
        licence.profile = application.applicant_profile
        licence.user = application.applicant_profile.user

        filename = '%s.pdf' % application.lodgement_number

        application.customer_status = 'approved'
        application.processing_status = 'issued'
        application.licence = licence

        response = HttpResponse(content_type='application/pdf')

        response.write(create_licence_pdf_bytes(filename, licence, application))

        return response
