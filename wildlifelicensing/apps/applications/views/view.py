from django.http import JsonResponse
from django.views.generic.base import TemplateView, View
from django.shortcuts import get_object_or_404

from preserialize.serialize import serialize

from wildlifelicensing.apps.applications.models import Application, Assessment, ApplicationLogEntry
from wildlifelicensing.apps.applications.mixins import UserCanViewApplicationMixin, CanPerformAssessmentMixin
from wildlifelicensing.apps.applications.utils import convert_documents_to_url, append_app_document_to_schema_data, \
    format_application, format_assessment
from wildlifelicensing.apps.main.models import Document
from wildlifelicensing.apps.main.forms import CommunicationsLogEntryForm
from wildlifelicensing.apps.main.helpers import is_officer
from wildlifelicensing.apps.main.utils import format_communications_log_entry
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder


class ViewReadonlyView(UserCanViewApplicationMixin, TemplateView):
    template_name = 'wl/view/view_readonly.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        if application.hard_copy is not None:
            application.licence_type.application_schema, application.data = \
                append_app_document_to_schema_data(application.licence_type.application_schema, application.data,
                                                   application.hard_copy.file.url)

        convert_documents_to_url(application.data, application.documents.all(), '')

        kwargs['application'] = application

        if is_officer(self.request.user):
            kwargs['customer'] = application.applicant

            if application.proxy_applicant is None:
                to = application.applicant.email
            else:
                to = application.proxy_applicant.email

            kwargs['log_entry_form'] = CommunicationsLogEntryForm(to=to, fromm=self.request.user.email)

        return super(ViewReadonlyView, self).get_context_data(**kwargs)


class AssessorConditionsView(CanPerformAssessmentMixin, TemplateView):
    template_name = 'wl/view/assessor_conditions_read_only.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        if application.hard_copy is not None:
            application.licence_type.application_schema, application.data = \
                append_app_document_to_schema_data(application.licence_type.application_schema, application.data,
                                                   application.hard_copy.file.url)

        convert_documents_to_url(application.data, application.documents.all(), '')

        kwargs['application'] = serialize(application, posthook=format_application)
        kwargs['form_structure'] = application.licence_type.application_schema

        assessment = get_object_or_404(Assessment, pk=self.args[1])

        kwargs['assessment'] = serialize(assessment, post_hook=format_assessment)

        return super(AssessorConditionsView, self).get_context_data(**kwargs)


class ApplicationLogListView(OfficerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=args[0])
        data = serialize(ApplicationLogEntry.objects.filter(application=application),
                         posthook=format_communications_log_entry,
                         exclude=['application', 'communicationslogentry_ptr', 'customer', 'officer']),

        return JsonResponse({'data': data[0]}, safe=False, encoder=WildlifeLicensingJSONEncoder)


class AddApplicationLogEntryView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = CommunicationsLogEntryForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            application = get_object_or_404(Application, pk=args[0])

            customer = application.applicant

            officer = request.user

            document = None

            if request.FILES and 'attachment' in request.FILES:
                document = Document.objects.create(file=request.FILES['attachment'])

            kwargs = {
                'document': document,
                'officer': officer,
                'customer': customer,
                'application': application,
                'type': form.cleaned_data['type'],
                'text': form.cleaned_data['text'],
                'subject': form.cleaned_data['subject'],
                'to': form.cleaned_data['to'],
                'fromm': form.cleaned_data['fromm']
            }

            ApplicationLogEntry.objects.create(**kwargs)

            return JsonResponse('ok', safe=False, encoder=WildlifeLicensingJSONEncoder)
        else:
            return JsonResponse(
                {
                    "errors": [
                        {
                            'status': "422",
                            'title': 'Data not valid',
                            'detail': form.errors
                        }
                    ]
                },
                safe=False, encoder=WildlifeLicensingJSONEncoder, status_code=422)
