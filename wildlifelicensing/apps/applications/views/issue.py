import os

from django.contrib import messages
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView

from preserialize.serialize import serialize

from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.forms import IssueLicenceForm
from wildlifelicensing.apps.main.pdf import create_licence_pdf_document, create_licence_pdf_bytes,\
    create_cover_letter_pdf_document
from wildlifelicensing.apps.main.signals import licence_issued
from wildlifelicensing.apps.applications.models import Application, Assessment
from wildlifelicensing.apps.applications.utils import format_application
from wildlifelicensing.apps.applications.emails import send_licence_issued_email


APPLICATION_SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

LICENCE_TYPE_NUM_CHARS = 2
LICENCE_NUMBER_NUM_CHARS = 6


class IssueLicenceView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/issue/issue_licence.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        kwargs['application'] = serialize(application, posthook=format_application)

        # if reissue
        if application.licence:
            kwargs['issue_licence_form'] = IssueLicenceForm(instance=application.licence)
        else:
            purposes = '\n\n'.join(Assessment.objects.filter(application=application).values_list('purpose', flat=True))

            kwargs['issue_licence_form'] = IssueLicenceForm(purpose=purposes, is_renewable=application.licence_type.is_renewable)

        return super(IssueLicenceView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        original_issue_date = None
        if application.licence is not None:
            issue_licence_form = IssueLicenceForm(request.POST, instance=application.licence)
            original_issue_date = application.licence.issue_date
        else:
            issue_licence_form = IssueLicenceForm(request.POST)

        if issue_licence_form.is_valid():
            licence = issue_licence_form.save(commit=False)
            licence.licence_type = application.licence_type
            licence.profile = application.applicant_profile
            licence.holder = application.applicant_profile.user
            licence.issuer = request.user

            if application.previous_application is not None:
                licence.licence_number = application.previous_application.licence.licence_number

                # if licence is renewal, want to use previous licence's sequence number
                if licence.licence_sequence == 0:
                    licence.licence_sequence = application.previous_application.licence.licence_sequence

            if not licence.licence_number:
                licence.save(no_revision=True)
                licence.licence_number = '%s-%s' % (str(licence.licence_type.pk).zfill(LICENCE_TYPE_NUM_CHARS),
                                                    str(licence.id).zfill(LICENCE_NUMBER_NUM_CHARS))

            licence.licence_sequence += 1

            licence_filename = 'licence-%s-%d.pdf' % (licence.licence_number, licence.licence_sequence)

            licence.licence_document = create_licence_pdf_document(licence_filename, licence, application,
                                                                   request.build_absolute_uri(reverse('home')),
                                                                   original_issue_date)

            cover_letter_filename = 'cover-letter-%s-%d.pdf' % (licence.licence_number, licence.licence_sequence)

            licence.cover_letter_document = create_cover_letter_pdf_document(cover_letter_filename, licence,
                                                                             request.build_absolute_uri(reverse('home')))

            licence.save()

            licence_issued.send(sender=self.__class__, wildlife_licence=licence)

            application.customer_status = 'approved'
            application.processing_status = 'issued'
            application.licence = licence

            application.save()

            # The licence should be emailed to the customer if they applied for it online. If an officer entered
            # the application on their behalf, the licence needs to be posted to the user.
            if application.proxy_applicant is None:
                # customer applied online
                messages.success(request, 'The licence has now been issued and sent as an email attachment to the '
                                 'licencee.')
                send_licence_issued_email(licence, application, request)
            else:
                # customer applied offline
                messages.success(request, 'The licence has now been issued and must be posted to the licencee. Click '
                                 'this link to show the licence <a href="{0}" target="_blank">Licence PDF'
                                 '</a><img height="20px" src="{1}"></img> and this link to show the cover letter '
                                 '<a href="{2}" target="_blank">Cover Letter PDF</a><img height="20px" src="{3}">'
                                 '</img>'.format(licence.licence_document.file.url, static('wl/img/pdf.png'),
                                                 licence.cover_letter_document.file.url, static('wl/img/pdf.png')))

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

        original_issue_date = None
        if application.licence is not None:
            issue_licence_form = IssueLicenceForm(request.GET, instance=application.licence)
            original_issue_date = application.licence.issue_date
        else:
            issue_licence_form = IssueLicenceForm(request.GET)

        licence = issue_licence_form.save(commit=False)
        licence.licence_type = application.licence_type
        licence.profile = application.applicant_profile
        licence.holder = application.applicant_profile.user

        filename = '%s.pdf' % application.lodgement_number

        application.customer_status = 'approved'
        application.processing_status = 'issued'
        application.licence = licence

        response = HttpResponse(content_type='application/pdf')

        response.write(create_licence_pdf_bytes(filename, licence, application,
                                                request.build_absolute_uri(reverse('home')),
                                                original_issue_date))

        return response
