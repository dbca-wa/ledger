import json
import os
import tempfile
import shutil

from datetime import datetime

from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files import File
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from ledger.accounts.models import Profile
from ledger.accounts.models import Document
from ledger.accounts.forms import AddressForm, ProfileForm

from wildlifelicensing.apps.main.models import WildlifeLicenceType
from wildlifelicensing.apps.main.forms import IdentificationForm

from wildlifelicensing.apps.applications.models import Application, AmendmentRequest
from wildlifelicensing.apps.applications.utils import create_data_from_form, get_all_filenames_from_application_data, \
    delete_application_session_data
from wildlifelicensing.apps.applications.forms import ProfileSelectionForm
from wildlifelicensing.apps.applications.mixins import UserCanEditApplicationMixin

APPLICATION_SCHEMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class SelectLicenceTypeView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/entry/select_licence_type.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        # if we've arrived at the licence type selection page and there is hangover application data left in the session, delete it
        delete_application_session_data(request.session)

        request.session['application'] = {}

        context = {'licence_types': dict(
            [(licence_type.code, licence_type.name) for licence_type in WildlifeLicenceType.objects.all()])}

        return render(request, self.template_name, context)


class EditApplicationView(UserCanEditApplicationMixin, View):
    def get(self, request, *args, **kwargs):
        delete_application_session_data(request.session)

        application = get_object_or_404(Application, pk=args[1]) if len(args) > 1 else None
        if application is not None and 'application' not in request.session:
            request.session['application'] = {}
            request.session['application']['profile'] = application.applicant_profile.id
            request.session['application']['data'] = application.data
            request.session.modified = True

        return redirect('applications:enter_details', *args, **kwargs)


class CheckIdentificationRequiredView(LoginRequiredMixin, FormView):
    template_name = 'wl/entry/upload_identification.html'
    login_url = '/'
    form_class = IdentificationForm

    def get(self, *args, **kwargs):
        licence_type = get_object_or_404(WildlifeLicenceType, code=args[1])

        if licence_type.identification_required and self.request.user.identification is None:
            return super(CheckIdentificationRequiredView, self).get(*args, **kwargs)
        else:
            return redirect('applications:create_select_profile', args[1], **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CheckIdentificationRequiredView, self).get_context_data(**kwargs)
        context['licence_type'] = get_object_or_404(WildlifeLicenceType, code=self.args[0])
        return context

    def form_valid(self, form):
        if self.request.user.identification is not None:
            self.request.user.identification.delete()

        self.request.user.identification = Document.objects.create(file=self.request.FILES['identification_file'])
        self.request.user.save()

        return redirect('applications:create_select_profile', *self.args)


class CreateSelectProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/entry/create_select_profile.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        context = {}

        if len(args) > 1:
            context['application_pk'] = args[1]

        profile_exists = request.user.profile_set.count() > 0

        if 'profile' in request.session.get('application'):
            selected_profile = Profile.objects.get(id=request.session.get('application').get('profile'))
            context['profile_selection_form'] = ProfileSelectionForm(user=request.user,
                                                                     selected_profile=selected_profile)
        else:
            if profile_exists:
                context['profile_selection_form'] = ProfileSelectionForm(user=request.user)

        if profile_exists:
            context['profile_creation_form'] = ProfileForm()
        else:
            context['profile_creation_form'] = ProfileForm(initial_display_name='Default',
                                                           initial_email=request.user.email)

        context['address_form'] = AddressForm()
        context['licence_type'] = get_object_or_404(WildlifeLicenceType, code=self.args[0])

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if 'select' in request.POST:
            profile_selection_form = ProfileSelectionForm(request.POST, user=request.user)

            if profile_selection_form.is_valid():
                request.session['application']['profile'] = profile_selection_form.cleaned_data.get('profile').id
                request.session.modified = True
            else:
                return render(request, self.template_name, {'profile_selection_form': profile_selection_form,
                                                            'profile_creation_form': ProfileForm(),
                                                            'address_form': AddressForm()})
        elif 'create' in request.POST:
            profile_form = ProfileForm(request.POST)
            address_form = AddressForm(request.POST)

            if profile_form.is_valid() and address_form.is_valid():
                profile = profile_form.save(commit=False)
                profile.postal_address = address_form.save()
                profile.user = request.user
                profile.save()

                request.session['application']['profile'] = profile.id
                request.session.modified = True
            else:
                return render(request, self.template_name,
                              {'profile_selection_form': ProfileSelectionForm(user=request.user),
                               'profile_creation_form': profile_form, 'address_form': address_form})

        return redirect('applications:enter_details', *args)


class EnterDetailsView(UserCanEditApplicationMixin, TemplateView):
    template_name = 'wl/entry/enter_details.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=args[1]) if len(args) > 1 else None

        licence_type = WildlifeLicenceType.objects.get(code=args[0])
        if request.session.get('application') and 'profile' in request.session.get('application'):
            profile = get_object_or_404(Profile, pk=request.session.get('application').get('profile'))
        else:
            profile = application.applicant_profile

        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, args[0])) as data_file:
            form_structure = json.load(data_file)

        context = {'licence_type': licence_type, 'profile': profile, 'structure': form_structure}

        if application is not None:
            context['application_pk'] = application.pk
            if application.review_status == 'awaiting_amendments':
                amendments = AmendmentRequest.objects.filter(application=application).filter(status='requested')
                context['amendments'] = amendments

        if request.session.get('application') and 'data' in request.session.get('application'):
            context['data'] = request.session.get('application').get('data')
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, args[0])) as data_file:
            form_structure = json.load(data_file)

        request.session['application']['data'] = create_data_from_form(form_structure, request.POST, request.FILES)
        request.session.modified = True

        if 'draft' in request.POST or 'draft_continue' in request.POST:
            if len(args) > 1:
                application = get_object_or_404(Application, pk=args[1])
            else:
                application = Application()

            application.data = request.session.get('application').get('data')
            application.licence_type = WildlifeLicenceType.objects.get(code=args[0])
            application.applicant_profile = get_object_or_404(Profile,
                                                              pk=request.session.get('application').get('profile'))
            application.customer_status = 'draft'
            application.processing_status = 'draft'
            application.save(version_user=request.user, version_comment='Details Modified')

            if 'files' in request.session.get('application') and os.path.exists(
                    request.session.get('application').get('files')):
                try:
                    for filename in get_all_filenames_from_application_data(form_structure,
                                                                            request.session.get('application').get(
                                                                                    'data')):
                        # need to be sure file is in tmp directory (as it could be a freshly attached file)
                        if os.path.exists(os.path.join(request.session.get('application').get('files'), filename)):
                            document = Document.objects.create(name=filename)
                            with open(os.path.join(request.session.get('application').get('files'), filename),
                                      'rb') as doc_file:
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

            if 'draft' in request.POST:
                delete_application_session_data(request.session)
                return redirect('dashboard:home')
            else:
                return redirect('applications:enter_details', args[0], application.pk)
        else:
            if len(request.FILES) > 0:
                if 'files' not in request.session.get('application'):
                    request.session['application']['files'] = tempfile.mkdtemp()
                    request.session.modified = True
                for f in request.FILES:
                    with open(os.path.join(request.session.get('application').get('files'), str(request.FILES[f])),
                              'wb+') as destination:
                        for chunk in request.FILES[f].chunks():
                            destination.write(chunk)

            return redirect('applications:preview', *args)


class PreviewView(UserCanEditApplicationMixin, TemplateView):
    template_name = 'wl/entry/preview.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, args[0])) as data_file:
            form_stucture = json.load(data_file)

        application = get_object_or_404(Application, pk=args[1]) if len(args) > 1 else None
        licence_type = WildlifeLicenceType.objects.get(code=args[0])
        if request.session.get('application') and 'profile' in request.session.get('application'):
            profile = get_object_or_404(Profile, pk=request.session.get('application').get('profile'))
        else:
            profile = application.applicant_profile

        context = {'structure': form_stucture, 'licence_type': licence_type, 'profile': profile}

        if len(args) > 1:
            context['application_pk'] = args[1]

        if request.session.get('application') and 'data' in request.session.get('application'):
            context['data'] = request.session.get('application').get('data')
        else:
            context['data'] = application.data

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (APPLICATION_SCHEMA_PATH, args[0])) as data_file:
            form_structure = json.load(data_file)

        if len(args) > 1:
            application = get_object_or_404(Application, pk=args[1])
        else:
            application = Application()

        application.data = request.session.get('application').get('data')
        application.licence_type = get_object_or_404(WildlifeLicenceType, code=args[0])
        application.correctness_disclaimer = request.POST.get('correctnessDisclaimer', '') == 'on'
        application.further_information_disclaimer = request.POST.get('furtherInfoDisclaimer', '') == 'on'
        application.applicant_profile = get_object_or_404(Profile, pk=request.session.get('application').get('profile'))
        application.lodgement_sequence += 1
        application.lodgement_date = datetime.now()
        if application.customer_status == 'amendment_required':
            # this is a 're-lodged' application after some amendment were required.
            # from this point we assumed that all the amendments have been amended.
            AmendmentRequest.objects.filter(application=application).filter(status='requested').update(status='amended')
            application.customer_status = 'under_review'
            application.review_status = 'amended'
            application.processing_status = 'ready_for_action'
        else:
            application.customer_status = 'pending'
            application.processing_status = 'new'

        if len(application.lodgement_number) == 0:
            application.save(no_revision=True)
            application.lodgement_number = str(application.id).zfill(9)

        application.save(version_user=request.user, version_comment='Details Modified')

        # if attached files were saved temporarily, add each to application as part of a Document
        if 'files' in request.session.get('application') and os.path.exists(
                request.session.get('application').get('files')):
            try:
                for filename in get_all_filenames_from_application_data(form_structure,
                                                                        request.session.get('application_data')):
                    document = Document.objects.create(name=filename)
                    with open(os.path.join(request.session.get('application').get('files'), filename),
                              'rb') as doc_file:
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
