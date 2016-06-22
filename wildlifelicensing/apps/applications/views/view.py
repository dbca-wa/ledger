import json
import os

from django.http import JsonResponse
from django.views.generic.base import TemplateView, View
from django.shortcuts import get_object_or_404

from preserialize.serialize import serialize

from wildlifelicensing.apps.applications.models import Application, ApplicationLogEntry
from wildlifelicensing.apps.applications.mixins import UserCanViewApplicationMixin
from wildlifelicensing.apps.applications.utils import convert_application_data_files_to_url
from wildlifelicensing.apps.main.models import Document
from wildlifelicensing.apps.main.forms import CommunicationsLogEntryForm
from wildlifelicensing.apps.main.helpers import is_officer
from wildlifelicensing.apps.main.utils import format_communications_log_entry
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder

APPLICATION_SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class ViewReadonlyView(UserCanViewApplicationMixin, TemplateView):
    template_name = 'wl/view/view_readonly.html'

    def get_context_data(self, **kwargs):
        application = get_object_or_404(Application, pk=self.args[0])

        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, application.licence_type.code_slug)) as data_file:
            form_structure = json.load(data_file)

        kwargs['licence_type'] = application.licence_type
        kwargs['structure'] = form_structure

        convert_application_data_files_to_url(form_structure, application.data, application.documents.all())

        kwargs['application'] = application

        if is_officer(self.request.user):
            kwargs['customer'] = application.applicant_profile.user
            kwargs['log_entry_form'] = CommunicationsLogEntryForm()

        return super(ViewReadonlyView, self).get_context_data(**kwargs)


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

            if application.proxy_applicant is None:
                customer = application.applicant_profile.user
            else:
                customer = application.proxy_applicant

            officer = request.user

            document = None

            if request.FILES and 'attachment' in request.FILES:
                document = Document.objects.create(file=request.FILES['attachment'])

            kwargs = {
                'document': document,
                'officer': officer,
                'customer': customer,
                'application': application,
                'text': form.cleaned_data['text'],
                'subject': form.cleaned_data['subject'],
                'to': format.cleanred_data['to'],
                'fromm': format.cleanred_data['fromm']
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
