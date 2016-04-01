import json
import os
import tempfile
import shutil

from datetime import datetime

from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files import File
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from ledger.accounts.models import Persona
from ledger.accounts.models import Document
from ledger.accounts.forms import AddressForm, PersonaForm

from wildlifelicensing.apps.main.models import WildlifeLicenceType

from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.applications.utils import create_data_from_form, get_all_filenames_from_application_data
from wildlifelicensing.apps.applications.forms import PersonaSelectionForm


APPLICATION_SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class SelectLicenceTypeView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/entry/select_licence_type.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        # if we've arrived at the licence type selection page and there is hangover application data left in the session, delete it
        delete_application_session_data(request.session)
        request.session['application'] = {}

        context = {'licence_types': dict([(licence_type.code, licence_type.name) for licence_type in WildlifeLicenceType.objects.all()])}

        return render(request, self.template_name, context)


class CreateSelectPersonaView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/entry/create_select_persona.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        context = {}

        if len(args) > 1:
            context['application_pk'] = args[1]

        persona_exists = request.user.persona_set.count() > 0

        if 'persona' in request.session.get('application'):
            selected_persona = Persona.objects.get(id=request.session.get('application').get('persona'))
            context['persona_selection_form'] = PersonaSelectionForm(user=request.user, selected_persona=selected_persona)
        else:
            if persona_exists:
                context['persona_selection_form'] = PersonaSelectionForm(user=request.user)

        if persona_exists:
            context['persona_creation_form'] = PersonaForm()
        else:
            context['persona_creation_form'] = PersonaForm(initial_display_name='Default', initial_email=request.user.email)

        context['address_form'] = AddressForm()

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if 'select' in request.POST:
            persona_selection_form = PersonaSelectionForm(request.POST, user=request.user)

            if persona_selection_form.is_valid():
                request.session['application']['persona'] = persona_selection_form.cleaned_data.get('persona').id
                request.session.modified = True
            else:
                return render(request, self.template_name, {'persona_selection_form': persona_selection_form,
                                                            'persona_creation_form': PersonaForm(),
                                                            'address_form': AddressForm()})
        elif 'create' in request.POST:
            persona_form = PersonaForm(request.POST)
            address_form = AddressForm(request.POST)

            if persona_form.is_valid() and address_form.is_valid():
                persona = persona_form.save(commit=False)
                persona.postal_address = address_form.save()
                persona.user = request.user
                persona.save()

                request.session['application']['persona'] = persona.id
                request.session.modified = True
            else:
                return render(request, self.template_name, {'persona_selection_form': PersonaSelectionForm(user=request.user),
                                                            'persona_creation_form': persona_form, 'address_form': address_form})

        return redirect('applications:enter_details', *args)


class EnterDetailsView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/entry/enter_details.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        if len(args) > 1 and 'application' not in request.session:
            application = get_object_or_404(Application, pk=args[1])
            request.session['application'] = {}
            request.session['application']['persona'] = application.applicant_persona.id
            request.session['application']['data'] = application.data
            request.session.modified = True

        licence_type = WildlifeLicenceType.objects.get(code=args[0])
        persona = Persona.objects.get(id=request.session.get('application').get('persona'))

        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, args[0])) as data_file:
            form_structure = json.load(data_file)

        context = {'licence_type': licence_type, 'persona': persona, 'structure': form_structure}

        if len(args) > 1:
            context['application_pk'] = args[1]

        if 'data' in request.session.get('application'):
            context['data'] = request.session.get('application').get('data')

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, args[0])) as data_file:
            form_structure = json.load(data_file)

        request.session['application']['data'] = create_data_from_form(form_structure, request.POST, request.FILES)
        request.session.modified = True

        if 'draft' in request.POST:
            if len(args) > 1:
                application = get_object_or_404(Application, pk=args[1])
            else:
                application = Application()

            application.data = request.session.get('application').get('data')
            application.licence_type = WildlifeLicenceType.objects.get(code=args[0])
            application.applicant_persona = Persona.objects.get(id=request.session.get('application').get('persona'))
            application.customer_status = 'draft'
            application.processing_status = 'draft'
            application.save()

            if 'files' in request.session.get('application') and os.path.exists(request.session.get('application').get('files')):
                try:
                    for filename in get_all_filenames_from_application_data(form_structure, request.session.get('application').get('data')):
                        # need to be sure file is in tmp directory (as it could be a freshly attached file)
                        if os.path.exists(os.path.join(request.session.get('application').get('files'), filename)):
                            document = Document.objects.create(name=filename)
                            with open(os.path.join(request.session.get('application').get('files'), filename), 'rb') as doc_file:
                                document.file.save(filename, File(doc_file), save=True)
                                application.documents.add(document)
                except Exception as e:
                    messages.error(request, 'There was a problem appending applications files: %s' % e)
                finally:
                    try:
                        shutil.rmtree(request.session.get('application').get('files'))
                    except (shutil.Error, OSError) as e:
                        messages.warning(request, 'There was a problem deleting temporary files: %s' % e)

            for f in request.FILES:
                application.documents.add(Document.objects.create(name=f, file=request.FILES[f]))

            messages.warning(request, 'The application was saved to draft.')

            delete_application_session_data(request.session)

            return redirect('dashboard:home')
        else:
            if len(request.FILES) > 0:
                if 'files' not in request.session.get('application'):
                    request.session['application']['files'] = tempfile.mkdtemp()
                    request.session.modified = True
                for f in request.FILES:
                    with open(os.path.join(request.session.get('application').get('files'), str(request.FILES[f])), 'wb+') as destination:
                        for chunk in request.FILES[f].chunks():
                            destination.write(chunk)

            return redirect('applications:preview', *args)


class PreviewView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/entry/preview.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, args[0])) as data_file:
            form_stucture = json.load(data_file)

        licence_type = WildlifeLicenceType.objects.get(code=args[0])
        persona = Persona.objects.get(id=request.session.get('application').get('persona'))

        context = {'structure': form_stucture, 'licence_type': licence_type, 'persona': persona}

        if len(args) > 1:
            context['application_pk'] = args[1]

        context['data'] = request.session.get('application').get('data')

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, args[0])) as data_file:
            form_structure = json.load(data_file)

        if len(args) > 1:
            application = get_object_or_404(Application, pk=args[1])
        else:
            application = Application()

        application.data = request.session.get('application').get('data')
        application.licence_type = WildlifeLicenceType.objects.get(code=args[0])
        application.applicant_persona = Persona.objects.get(id=request.session.get('application').get('persona'))
        application.lodged_date = datetime.now()
        application.customer_status = 'pending'
        application.processing_status = 'new'
        application.save()

        # if attached files were saved temporarily, add each to application as part of a Document
        if 'files' in request.session.get('application') and os.path.exists(request.session.get('application').get('files')):
            try:
                for filename in get_all_filenames_from_application_data(form_structure, request.session.get('application_data')):
                    document = Document.objects.create(name=filename)
                    with open(os.path.join(request.session.get('application').get('files'), filename), 'rb') as doc_file:
                        document.file.save(filename, File(doc_file), save=True)

                        application.documents.add(document)

                messages.success(request, 'The application was successfully lodged.')
            except Exception as e:
                messages.error(request, 'There was a problem creating the application: %s' % e)
            finally:
                try:
                    shutil.rmtree(request.session.get('application').get('files'))
                except (shutil.Error, OSError) as e:
                    messages.warning(request, 'There was a problem deleting temporary files: %s' % e)
        else:
            messages.success(request, 'The application was successfully lodged.')

        delete_application_session_data(request.session)

        return redirect('dashboard:home')


def delete_application_session_data(session):
    if 'application' in session:
        if 'files' in session['application']:
            if os.path.exists(session.get('application').get('files')):
                try:
                    shutil.rmtree(session.get('application').get('files'))
                except:
                    pass

        del session['application']
