from datetime import datetime

from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from ledger.accounts.models import EmailUser, Document
from ledger.accounts.forms import EmailUserForm, AddressForm, ProfileForm

from wildlifelicensing.apps.main.models import WildlifeLicenceType,\
    WildlifeLicenceCategory
from wildlifelicensing.apps.main.forms import IdentificationForm

from wildlifelicensing.apps.applications.models import Application, AmendmentRequest
from wildlifelicensing.apps.applications import utils
from wildlifelicensing.apps.applications.forms import ProfileSelectionForm
from wildlifelicensing.apps.applications.mixins import UserCanEditApplicationMixin,\
    UserCanViewApplicationMixin
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin, OfficerOrCustomerRequiredMixin
from wildlifelicensing.apps.main.helpers import is_officer, is_customer
from django.core.urlresolvers import reverse
from wildlifelicensing.apps.applications.utils import delete_session_application

LICENCE_TYPE_NUM_CHARS = 2
LODGEMENT_NUMBER_NUM_CHARS = 6


class ApplicationEntryBaseView(TemplateView):
    login_url = '/'

    def get_context_data(self, **kwargs):
        try:
            application = utils.get_session_application(self.request.session)
        except Exception as e:
            messages.error(self.request, e.message)
            return redirect('wl_applications:new_application')

        kwargs['licence_type'] = application.licence_type

        kwargs['customer'] = application.applicant

        kwargs['is_renewal'] = application.processing_status == 'renewal'
        kwargs['is_amendment'] = application.processing_status == 'licence_amendment'

        return super(ApplicationEntryBaseView, self).get_context_data(**kwargs)


class NewApplicationView(OfficerOrCustomerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        utils.remove_temp_applications_for_user(request.user)

        application = Application.objects.create()

        utils.set_session_application(request.session, application)

        if is_customer(request.user):
            application.applicant = request.user
            application.save()

            return redirect('wl_applications:select_licence_type', *args, **kwargs)
        else:
            application.proxy_applicant = request.user
            application.save()
            return redirect('wl_applications:create_select_customer')


class EditApplicationView(UserCanEditApplicationMixin, View):
    def get(self, request, *args, **kwargs):
        utils.remove_temp_applications_for_user(request.user)

        try:
            utils.set_session_application(request.session, Application.objects.get(id=args[0]))
        except:
            messages.error(self.request, 'Unable to find application')
            return redirect('wl_dashboard:home')

        return redirect('wl_applications:enter_details')


class RenewLicenceView(View):  # NOTE: need a UserCanRenewLicence type mixin
    def get(self, request, *args, **kwargs):
        utils.remove_temp_applications_for_user(request.user)

        previous_application = get_object_or_404(Application, licence=args[0])

        # check if there is already a renewal, otherwise create one
        try:
            application = Application.objects.get(previous_application=previous_application)
            if application.customer_status == 'under_review':
                messages.warning(request, 'A renewal for this licence has already been lodged and is awaiting review.')
                return redirect('wl_dashboard:home')
        except Application.DoesNotExist:
            application = utils.clone_application_with_status_reset(previous_application)
            application.processing_status = 'renewal'
            application.save()

        utils.set_session_application(request.session, application)

        return redirect('wl_applications:enter_details')


class AmendLicenceView(View):  # NOTE: need a UserCanRenewLicence type mixin
    def get(self, request, *args, **kwargs):
        utils.remove_temp_applications_for_user(request.user)

        previous_application = get_object_or_404(Application, licence=args[0])

        # check if there is already a renewal or amendment, otherwise create one
        try:
            application = Application.objects.get(previous_application=previous_application)
            if application.customer_status == 'under_review':
                messages.warning(request, 'An amendment for this licence has already been lodged and is awaiting review.')
                return redirect('wl_dashboard:home')
        except Application.DoesNotExist:
            application = utils.clone_application_with_status_reset(previous_application, keep_invoice=True)
            application.processing_status = 'licence_amendment'
            application.save()

        utils.set_session_application(request.session, application)

        return redirect('wl_applications:enter_details')


class CreateSelectCustomer(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/entry/create_select_customer.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        kwargs['create_customer_form'] = EmailUserForm(email_required=False)

        return super(CreateSelectCustomer, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        try:
            application = utils.get_session_application(request.session)
        except Exception as e:
            messages.error(request, e.message)
            return redirect('wl_applications:new_application')

        if 'select' in request.POST:
            application.applicant = EmailUser.objects.get(id=request.POST.get('customer'))
            application.save()
        elif 'create' in request.POST:
            create_customer_form = EmailUserForm(request.POST, email_required=False)
            if create_customer_form.is_valid():
                customer = create_customer_form.save()
                application.applicant = customer
                application.save()
            else:
                context = {'create_customer_form': create_customer_form}
                return render(request, self.template_name, context)

        return redirect('wl_applications:select_licence_type', *args, **kwargs)


class SelectLicenceTypeView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/entry/select_licence_type.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        if args:
            try:
                application = utils.get_session_application(self.request.session)
            except Exception as e:
                messages.error(self.request, e.message)
                return redirect('wl_applications:new_application')

            application.licence_type = WildlifeLicenceType.objects.get(code_slug=self.args[0])
            application.save()

            return redirect('wl_applications:check_identification')

        categories = {}

        for category in WildlifeLicenceCategory.objects.all():
            categories[category.name] = WildlifeLicenceType.objects.\
                filter(category=category, replaced_by__isnull=True).values('code_slug',
                                                                           'name', 'code')

        if WildlifeLicenceType.objects.filter(category__isnull=True, replaced_by__isnull=True).exists():
            categories['Other'] = WildlifeLicenceType.objects.\
                filter(category__isnull=True, replaced_by__isnull=True).values('code_slug', 'name', 'code')

        return render(request, self.template_name, {'licence_categories': categories})


class CheckIdentificationRequiredView(LoginRequiredMixin, ApplicationEntryBaseView, FormView):
    template_name = 'wl/entry/upload_identification.html'
    form_class = IdentificationForm

    def get(self, *args, **kwargs):
        try:
            application = utils.get_session_application(self.request.session)
        except Exception as e:
            messages.error(self.request, e.message)
            return redirect('wl_applications:new_application')

        if application.licence_type.identification_required and application.applicant.identification is None:
            return super(CheckIdentificationRequiredView, self).get(*args, **kwargs)
        else:
            return redirect('wl_applications:create_select_profile')

    def get_context_data(self, **kwargs):
        kwargs['file_types'] = ', '.join(['.' + file_ext for file_ext in IdentificationForm.VALID_FILE_TYPES])

        return super(CheckIdentificationRequiredView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        try:
            application = utils.get_session_application(self.request.session)
        except Exception as e:
            messages.error(self.request, e.message)
            return redirect('wl_applications:new_application')

        if application.applicant.identification is not None:
            application.applicant.identification.delete()

        application.applicant.identification = Document.objects.create(file=self.request.FILES['identification_file'])
        application.applicant.save()

        # update any other applications for this user that are awaiting ID upload
#       for application in Application.objects.filter(applicant_profile__user=applicant):
        for app in Application.objects.filter(applicant=application.applicant):
            if app.id_check_status == 'awaiting_update':
                app.id_check_status = 'updated'
                app.save()

        return redirect('wl_applications:create_select_profile', *self.args)


class CreateSelectProfileView(LoginRequiredMixin, ApplicationEntryBaseView):
    template_name = 'wl/entry/create_select_profile.html'

    def get_context_data(self, **kwargs):
        try:
            application = utils.get_session_application(self.request.session)
        except Exception as e:
            messages.error(self.request, e.message)
            return redirect('wl_applications:new_application')

        kwargs['application_pk'] = application.id

        profile_exists = application.applicant.profile_set.count() > 0

        if application.applicant_profile is not None:
            kwargs['profile_selection_form'] = ProfileSelectionForm(user=application.applicant,
                                                                    selected_profile=application.applicant_profile)
        else:
            if profile_exists:
                kwargs['profile_selection_form'] = ProfileSelectionForm(user=application.applicant)

        if profile_exists:
            kwargs['profile_creation_form'] = ProfileForm(user=application.applicant)
        else:
            kwargs['profile_creation_form'] = ProfileForm(initial_display_name='Default',
                                                          initial_email=application.applicant.email,
                                                          user=application.applicant)

        kwargs['address_form'] = AddressForm()

        return super(CreateSelectProfileView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        try:
            application = utils.get_session_application(request.session)
        except Exception as e:
            messages.error(self.request, e.message)
            return redirect('wl_applications:new_application')

        if 'select' in request.POST:
            profile_selection_form = ProfileSelectionForm(request.POST, user=application.applicant)

            if profile_selection_form.is_valid():
                application.applicant_profile = profile_selection_form.cleaned_data.get('profile')
                application.save()
            else:
                return render(request, self.template_name, {'licence_type': application.licence_type,
                                                            'profile_selection_form': profile_selection_form,
                                                            'profile_creation_form': ProfileForm(),
                                                            'address_form': AddressForm()})
        elif 'create' in request.POST:
            profile_form = ProfileForm(request.POST)
            address_form = AddressForm(request.POST)

            if profile_form.is_valid() and address_form.is_valid():
                profile = profile_form.save(commit=False)
                profile.postal_address = address_form.save()
                profile.save()

                application.applicant_profile = profile
                application.save()
            else:
                return render(request, self.template_name,
                              {'licence_type': application.licence_type,
                               'profile_selection_form': ProfileSelectionForm(user=request.user),
                               'profile_creation_form': profile_form, 'address_form': address_form})

        return redirect('wl_applications:enter_details')


class EnterDetailsView(UserCanEditApplicationMixin, ApplicationEntryBaseView):
    template_name = 'wl/entry/enter_details.html'

    def get_context_data(self, **kwargs):
        try:
            application = utils.get_session_application(self.request.session)
        except Exception as e:
            messages.error(self.request, e.message)
            return redirect('wl_applications:new_application')

        kwargs['licence_type'] = application.licence_type
        kwargs['profile'] = application.applicant_profile
        kwargs['structure'] = application.licence_type.application_schema

        kwargs['is_proxy_applicant'] = is_officer(self.request.user)

        if application.review_status == 'awaiting_amendments':
            amendments = AmendmentRequest.objects.filter(application=application).filter(status='requested')
            kwargs['amendments'] = amendments

        if application.hard_copy is not None:
            kwargs['application_document'] = application.hard_copy.file.url

        if application.data:
            utils.convert_documents_to_url(application.data, application.documents.all(), '')

        kwargs['data'] = application.data

        return super(EnterDetailsView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        try:
            application = utils.get_session_application(self.request.session)
        except Exception as e:
            messages.error(self.request, e.message)
            return redirect('wl_applications:new_application')

        application.data = utils.create_data_from_form(application.licence_type.application_schema,
                                                       request.POST, request.FILES)

        for f in request.FILES:
            if f == 'application_document':
                if application.hard_copy is None:
                    application.hard_copy = Document.objects.create(name='hard_copy')
                application.hard_copy.file = request.FILES[f]
                application.hard_copy.save()
            else:
                # for legacy applications, need to check if there's a document where file is
                # named by the file name rather than the form field name
                try:
                    document = application.documents.get(name=str(request.FILES[f]))
                except Document.DoesNotExist:
                    document = application.documents.get_or_create(name=f)[0]

                document.name = f
                document.file = request.FILES[f]

                document.save()

        application.save()

        if 'draft' in request.POST or 'draft_continue' in request.POST:
            application.customer_status = 'draft'

            if application.processing_status != 'renewal':
                application.processing_status = 'draft'

            application.save()

            messages.warning(request, 'The application was saved to draft.')

            if 'draft' in request.POST:
                utils.delete_session_application(request.session)
                return redirect('wl_dashboard:home')
            else:
                return redirect('wl_applications:enter_details')
        else:
            return redirect('wl_applications:preview')


class PreviewView(UserCanEditApplicationMixin, ApplicationEntryBaseView):
    template_name = 'wl/entry/preview.html'

    def get_context_data(self, **kwargs):
        try:
            application = utils.get_session_application(self.request.session)
        except Exception as e:
            messages.error(self.request, e.message)
            return redirect('wl_applications:new_application')

        kwargs['profile'] = application.applicant_profile
        kwargs['structure'] = application.licence_type.application_schema

        kwargs['is_proxy_applicant'] = is_officer(self.request.user)

        if application.data:
            utils.convert_documents_to_url(application.data, application.documents.all(), '')

        if application.hard_copy is not None:
            kwargs['structure'], kwargs['data'] = utils.append_app_document_to_schema_data(kwargs['structure'],
                                                                                           application.data,
                                                                                           application.hard_copy.file.url)
        else:
            kwargs['data'] = application.data

        return super(PreviewView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        try:
            application = utils.get_session_application(self.request.session)
        except Exception as e:
            messages.error(self.request, e.message)
            return redirect('wl_applications:new_application')

        application.correctness_disclaimer = request.POST.get('correctnessDisclaimer', '') == 'on'
        application.further_information_disclaimer = request.POST.get('furtherInfoDisclaimer', '') == 'on'

        application.lodgement_sequence += 1
        application.lodgement_date = datetime.now().date()

        if application.customer_status == 'amendment_required':
            # this is a 're-lodged' application after some amendment were required.
            # from this point we assume that all the amendments have been amended.
            AmendmentRequest.objects.filter(application=application).filter(status='requested').update(status='amended')
            application.review_status = 'amended'
            application.processing_status = 'ready_for_action'
        elif application.processing_status != 'renewal' and application.processing_status != 'licence_amendment':
            application.processing_status = 'new'

        application.customer_status = 'under_review'

        if not application.lodgement_number:
            application.lodgement_number = '%s-%s' % (str(application.licence_type.pk).zfill(LICENCE_TYPE_NUM_CHARS),
                                                      str(application.pk).zfill(LODGEMENT_NUMBER_NUM_CHARS))

        application.save(version_user=application.applicant, version_comment='Details Modified')

        return redirect(reverse('wl_payments:checkout_application', args=[application.pk]))


class ApplicationCompleteView(UserCanViewApplicationMixin, ApplicationEntryBaseView):
    template_name = 'wl/entry/complete.html'

    def get(self, request, *args, **kwargs):
        try:
            application = utils.get_session_application(self.request.session)
        except Exception as e:
            messages.error(self.request, e.message)
            return redirect('wl_applications:new_application')

        application.invoice_reference = request.GET.get('invoice')

        application.save()

        delete_session_application(request.session)

        return render(request, self.template_name, {'application': application})
