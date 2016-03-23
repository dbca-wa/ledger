import json
import os
import tempfile
import shutil

from django.views.generic.base import TemplateView, View
from django.shortcuts import render, redirect
from django.core.context_processors import csrf
from django.core.files import File
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http.response import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from ledger.accounts.models import EmailUser
from ledger.accounts.models import Document

from models import Application
from utils import create_data_from_form, get_all_filenames_from_application_data
from wildlifelicensing.apps.applications.forms import PersonaSelectionForm
from ledger.accounts.forms import AddressForm, PersonaForm
from bottle import Request


class ApplicationsView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/applications.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ApplicationsView, self).get_context_data(**kwargs)
        context['applications'] = {'regulation17': 'Application for a licence to take fauna for scientific purposes'}

        return context


class PersonaCreationSelectionView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/persona_creation_selection.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        context = {}

        if request.user.persona_set.count() > 0:
            context['persona_selection_form'] = PersonaSelectionForm(user=request.user)

        context['persona_creation_form'] = PersonaForm()
        context['address_form'] = AddressForm()

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if 'select' in request.POST:
            persona_selection_form = PersonaSelectionForm(request.POST, user=request.user)

            if persona_selection_form.is_valid():
                request.session['applicant_persona'] = persona_selection_form.cleaned_data.get('persona').id
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

                request.session['applicant_persona'] = persona.id
            else:
                return render(request, self.template_name, {'persona_selection_form': PersonaSelectionForm(user=request.user),
                                                            'persona_creation_form': persona_form, 'address_form': address_form})

        return redirect('applications:application', args[0])


class ApplicationView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/application.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_structure = json.load(data_file)

        context = {'structure': form_structure, 'application_type': args[0]}
        context.update(csrf(request))

        if request.GET.get('editing', '') == 'true':
            context['data'] = request.session.get('application_data')
            if 'applicant' in request.session:
                context['data']['applicant'] = request.session['applicant']
        else:
            # if we've arrived at the application entry page and there is hangover data
            # left in the session, delete it
            delete_application_session_data(request.session)

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_structure = json.load(data_file)

        request.session['application_data'] = create_data_from_form(form_structure, request.POST, request.FILES)

        # if application is created on behalf of a user, get user ID from POST, otherwise use authenticated user
        if 'applicant' in request.POST:
            request.session['applicant'] = request.POST['applicant']
        else:
            request.session['applicant'] = request.user.id

        if 'draft' in request.POST:
            applicant = EmailUser.objects.get(id=request.session['applicant'])

            application = Application.objects.create(data=request.session.get('application_data'), applicant=applicant, state='draft')

            if 'application_files' in request.session and os.path.exists(request.session['application_files']):
                try:
                    for filename in get_all_filenames_from_application_data(form_structure, request.session.get('application_data')):
                        # need to be sure file is in tmp directory (as it could be a freshly attached file)
                        if os.path.exists(os.path.join(request.session['application_files'], filename)):
                            document = Document.objects.create(name=filename)
                            with open(os.path.join(request.session['application_files'], filename), 'rb') as doc_file:
                                document.file.save(filename, File(doc_file), save=True)
                                application.documents.add(document)
                except Exception as e:
                    messages.error(request, 'There was a problem appending applications files: %s' % e)
                finally:
                    try:
                        shutil.rmtree(request.session['application_files'])
                    except (shutil.Error, OSError) as e:
                        messages.warning(request, 'There was a problem deleting temporary files: %s' % e)

            for f in request.FILES:
                application.documents.add(Document.objects.create(name=f, file=request.FILES[f]))

            messages.warning(request, 'The application was saved to draft.')

            delete_application_session_data(request.session)

            return redirect('applications:applications')
        else:
            if len(request.FILES) > 0:
                if 'application_files' not in request.session:
                    request.session['application_files'] = tempfile.mkdtemp()
                for f in request.FILES:
                    with open(os.path.join(request.session['application_files'], str(request.FILES[f])), 'wb+') as destination:
                        for chunk in request.FILES[f].chunks():
                            destination.write(chunk)

            return redirect('applications:application_preview', args[0])


class ApplicationPreviewView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/application_preview.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_stucture = json.load(data_file)

        context = {'structure': form_stucture, 'application_type': args[0]}
        context.update(csrf(request))

        context['data'] = request.session.get('application_data')

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if 'edit' in request.POST:
            return redirect(reverse('applications:application', args=(args[0],)) + '?editing=true')

        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_structure = json.load(data_file)

        applicant = EmailUser.objects.get(id=request.session['applicant'])

        application = Application.objects.create(data=request.session.get('application_data'), applicant=applicant, state='lodged')

        # if attached files were saved temporarily, add each to application as part of a Document
        if 'application_files' in request.session and os.path.exists(request.session['application_files']):
            try:
                for filename in get_all_filenames_from_application_data(form_structure, request.session.get('application_data')):
                    document = Document.objects.create(name=filename)
                    with open(os.path.join(request.session['application_files'], filename), 'rb') as doc_file:
                        document.file.save(filename, File(doc_file), save=True)

                        application.documents.add(document)

                messages.success(request, 'The application was successfully lodged.')
            except Exception as e:
                messages.error(request, 'There was a problem creating the application: %s' % e)
            finally:
                try:
                    shutil.rmtree(request.session['application_files'])
                except (shutil.Error, OSError) as e:
                    messages.warning(request, 'There was a problem deleting temporary files: %s' % e)
        else:
            messages.success(request, 'The application was successfully lodged.')

        return redirect('applications:applications')


class ApplicantsView(LoginRequiredMixin, View):
    login_url = '/'

    def get(self, request, *args, **kwargs):
        if len(args) > 0:
            email_users = EmailUser.objects.filter(id=args[0])
        else:
            email_users = EmailUser.objects.filter(last_name__istartswith=request.GET.get('term', ''))

        applicants = []
        for user in email_users:
            applicants.append({'id': user.id, 'text': user.last_name + ', ' + user.first_name + ' (' + user.email + ')'})

        return JsonResponse(applicants, safe=False)


def delete_application_session_data(session):
    if 'application_data' in session:
        del session['application_data']
    if 'applicant' in session:
        del session['applicant']
    if 'application_files' in session:
        if os.path.exists(session['application_files']):
            try:
                shutil.rmtree(session['application_files'])
            except:
                pass

        del session['application_files']
