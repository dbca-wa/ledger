import json
import os
import tempfile
import shutil

from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect
from django.core.context_processors import csrf
from django.core.files import File
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from ledger.accounts.models import Persona
from ledger.accounts.models import Document

from models import Application
from utils import create_data_from_form, get_all_filenames_from_application_data
from wildlifelicensing.apps.applications.forms import PersonaSelectionForm
from ledger.accounts.forms import AddressForm, PersonaForm
from ledger.licence.models import LicenceType


class SelectLicenceTypeView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/select_licence_type.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        # if we've arrived at the licence type selection page and there is hangover application data left in the session, delete it
        delete_application_session_data(request.session)
        request.session['application'] = {}

        context = {'licence_types': dict([(licence_type.code, licence_type.name) for licence_type in LicenceType.objects.all()])}

        return render(request, self.template_name, context)


class CreateSelectPersonaView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/create_select_persona.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        context = {}

        if 'persona' in request.session.get('application'):
            selected_persona = Persona.objects.get(id=request.session.get('application').get('persona'))
            context['persona_selection_form'] = PersonaSelectionForm(user=request.user, selected_persona=selected_persona)
            print PersonaSelectionForm
        else:
            if request.user.persona_set.count() > 0:
                context['persona_selection_form'] = PersonaSelectionForm(user=request.user)

        context['persona_creation_form'] = PersonaForm()
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

        return redirect('applications:enter_details', args[0])


class EnterDetails(LoginRequiredMixin, TemplateView):
    template_name = 'wl/enter_details.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        licence_type = LicenceType.objects.get(code=args[0])
        persona = Persona.objects.get(id=request.session.get('application').get('persona'))

        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_structure = json.load(data_file)

        context = {'licence_type': licence_type, 'persona': persona, 'structure': form_structure}
        context.update(csrf(request))

        if 'data' in request.session.get('application'):
            context['data'] = request.session.get('application').get('data')

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_structure = json.load(data_file)

        request.session['application']['data'] = create_data_from_form(form_structure, request.POST, request.FILES)
        request.session.modified = True

        if 'draft' in request.POST:
            applicant_persona = Persona.objects.get(id=request.session.get('application').get('persona'))

            licence_type = LicenceType.objects.get(code=args[0])
            application = Application.objects.create(data=request.session.get('application').get('data'), licence_type=licence_type,
                                                     applicant_persona=applicant_persona, status='draft')

            if 'application_files' in request.session and os.path.exists(request.session.get('application').get('files')):
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

            return redirect('applications:select_licence_type')
        else:
            if len(request.FILES) > 0:
                if 'files' not in request.session.get('application'):
                    request.session['application']['files'] = tempfile.mkdtemp()
                    request.session.modified = True
                for f in request.FILES:
                    with open(os.path.join(request.session.get('application').get('files'), str(request.FILES[f])), 'wb+') as destination:
                        for chunk in request.FILES[f].chunks():
                            destination.write(chunk)

            return redirect('applications:preview', args[0])


class PreviewView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/preview.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_stucture = json.load(data_file)

        licence_type = LicenceType.objects.get(code=args[0])
        persona = Persona.objects.get(id=request.session.get('application').get('persona'))

        context = {'structure': form_stucture, 'licence_type': licence_type, 'persona': persona}
        context.update(csrf(request))

        context['data'] = request.session.get('application').get('data')

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_structure = json.load(data_file)

        applicant_persona = Persona.objects.get(id=request.session.get('application').get('persona'))

        licence_type = LicenceType.objects.get(code=args[0])

        application = Application.objects.create(data=request.session.get('application').get('data'), licence_type=licence_type,
                                                 applicant_persona=applicant_persona, status='lodged')

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

        return redirect('applications:select_licence_type')


def delete_application_session_data(session):
    if 'application' in session:
        if 'files' in session['application']:
            if os.path.exists(session.get('application').get('files')):
                try:
                    shutil.rmtree(session.get('application').get('files'))
                except:
                    pass

        del session['application']
