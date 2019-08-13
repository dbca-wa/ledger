from datetime import datetime

from django.views.generic.base import View, TemplateView
from django.views.generic.edit import FormView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponse, HttpResponseForbidden
from django.utils.http import urlencode
from django.core.urlresolvers import reverse

from ledger.accounts.models import EmailUser, Document
from ledger.accounts.forms import EmailUserForm, AddressForm, ProfileForm

from wildlifelicensing.apps.main.models import WildlifeLicenceType, \
    WildlifeLicenceCategory, Variant
from wildlifelicensing.apps.main.forms import IdentificationForm, SeniorCardForm
from wildlifelicensing.apps.applications.models import Application, AmendmentRequest, \
    ApplicationVariantLink, ApplicationUserAction
from wildlifelicensing.apps.applications import utils
from wildlifelicensing.apps.applications.forms import ProfileSelectionForm
from wildlifelicensing.apps.applications.mixins import UserCanEditApplicationMixin, UserCanViewApplicationMixin, \
    UserCanRenewApplicationMixin, UserCanAmendApplicationMixin, RedirectApplicationInSessionMixin, \
    RedirectApplicationNotInSessionMixin
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin, OfficerOrCustomerRequiredMixin
from wildlifelicensing.apps.main.helpers import is_customer, is_officer, render_user_name
from wildlifelicensing.apps.applications.utils import delete_session_application
from wildlifelicensing.apps.payments.utils import is_licence_free, get_licence_price, \
    generate_product_title

LICENCE_TYPE_NUM_CHARS = 2
LODGEMENT_NUMBER_NUM_CHARS = 6


class ApplicationEntryBaseView(RedirectApplicationNotInSessionMixin, TemplateView):
    login_url = '/'

    def get_context_data(self, **kwargs):
        application = utils.get_session_application(self.request.session)

        kwargs['licence_type'] = application.licence_type

        kwargs['variants'] = ' / '.join(application.variants.through.objects.filter(application=application).
                                        order_by('order').values_list('variant__name', flat=True))

        kwargs['customer'] = application.applicant

        kwargs['is_renewal'] = application.application_type == 'renewal'
        kwargs['is_amendment'] = application.application_type == 'amendment'

        return super(ApplicationEntryBaseView, self).get_context_data(**kwargs)


class DeleteApplicationSessionView(UserCanEditApplicationMixin, View):
    def post(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=request.POST.get('applicationId'))

        if not (application.applicant == request.user or application.proxy_applicant == request.user):
            return HttpResponseForbidden('Application does not belong to user or proxy application')

        session_application_id = utils.get_session_application(request.session)

        if session_application_id.id == application.id:
            utils.delete_session_application(request.session)

            if application.is_temporary:
                application.delete()

        return HttpResponse()


class NewApplicationView(OfficerOrCustomerRequiredMixin, RedirectApplicationInSessionMixin, View):
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


class EditApplicationView(UserCanEditApplicationMixin, RedirectApplicationInSessionMixin, View):
    def get(self, request, *args, **kwargs):
        utils.remove_temp_applications_for_user(request.user)

        try:
            utils.set_session_application(request.session, Application.objects.get(id=args[0]))
        except:
            messages.error(self.request, 'Unable to find application')
            return redirect('wl_dashboard:home')

        return redirect('wl_applications:enter_details')


class DiscardApplicationView(View, UserCanViewApplicationMixin):

    def get_and_check_application(self, request, *args):
        """
        Warning! Don't call this method get_application or it will clash with the one in the UserCanViewApplicationMixin
        """
        application = get_object_or_404(Application, pk=args[0])
        if not application.is_discardable:
            raise Exception('Application cannot be discarded at this stage')
        return application

    def get(self, request, *args, **kwargs):
        try:
            application = self.get_and_check_application(request, *args)
            # confirmation page context
            ctx = {
                'action_url': reverse('wl_applications:discard_application', args=[application.pk]),
                'cancel_url': reverse('wl_dashboard:home')
            }
            return render(request,
                          template_name='wl/entry/confirm_discard.html',
                          context=ctx)

        except Exception as e:
            messages.error(self.request, str(e))
            return redirect('wl_dashboard:home')

    def post(self, request, *args, **kwargs):
        """
        Two cases:
         1- If an application has been lodged/submitted its state becomes 'discarded'
         2- If it is a first time draft (not submitted) it is deleted.
        """
        try:
            application = self.get_and_check_application(request, *args)
            if application.is_deletable:
                application.delete()
            else:
                application.customer_status = application.processing_status = 'discarded'
                application.save()
                application.log_user_action(
                    ApplicationUserAction.ACTION_DISCARD_APPLICATION.format(application),
                    request
                )
            if application.lodgement_number:
                message = 'Application {} discarded'.format(application)
            else:
                message = 'Application discarded'
            messages.success(self.request, message)
        except Exception as e:
            messages.error(self.request, str(e))

        return redirect('wl_dashboard:home')


class RenewLicenceView(UserCanRenewApplicationMixin, RedirectApplicationInSessionMixin, View):
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
            application.application_type = 'renewal'
            if is_officer(request.user):
                application.proxy_applicant = request.user
            application.save()

        utils.set_session_application(request.session, application)

        return redirect('wl_applications:enter_details')


class AmendLicenceView(UserCanAmendApplicationMixin, RedirectApplicationInSessionMixin, View):
    def get(self, request, *args, **kwargs):
        utils.remove_temp_applications_for_user(request.user)

        previous_application = get_object_or_404(Application, licence=args[0])

        # check if there is already a renewal or amendment, otherwise create one
        try:
            application = Application.objects.get(previous_application=previous_application)
            if application.customer_status == 'under_review':
                messages.warning(request,
                                 'An amendment for this licence has already been lodged and is awaiting review.')
                return redirect('wl_dashboard:home')
        except Application.DoesNotExist:
            application = utils.clone_application_with_status_reset(previous_application, is_licence_amendment=True)
            application.application_type = 'amendment'
            if is_officer(request.user):
                application.proxy_applicant = request.user
            application.save()

        utils.set_session_application(request.session, application)

        return redirect('wl_applications:enter_details')


class CreateSelectCustomer(OfficerRequiredMixin, RedirectApplicationNotInSessionMixin, TemplateView):
    template_name = 'wl/entry/create_select_customer.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        kwargs['application'] = utils.get_session_application(self.request.session)

        kwargs['create_customer_form'] = EmailUserForm(email_required=False)

        return super(CreateSelectCustomer, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        application = utils.get_session_application(request.session)

        if 'select' in request.POST:
            application.applicant = EmailUser.objects.get(id=request.POST.get('customer'))
            application.save()
        elif 'create' in request.POST:
            create_customer_form = EmailUserForm(request.POST, email_required=False)
            if create_customer_form.is_valid():
                customer = create_customer_form.save()
                application.applicant = customer
                application.save()
                application.log_user_action(
                    ApplicationUserAction.ACTION_CREATE_CUSTOMER_.format(render_user_name(customer)),
                    request
                )
            else:
                context = {
                    'create_customer_form': create_customer_form, 
                    'application': application
                }
                return render(request, self.template_name, context)

        return redirect('wl_applications:select_licence_type', *args, **kwargs)


class SelectLicenceTypeView(LoginRequiredMixin, RedirectApplicationNotInSessionMixin, TemplateView):
    template_name = 'wl/entry/select_licence_type.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        application = utils.get_session_application(self.request.session)

        if args:
            application.licence_type = WildlifeLicenceType.objects.get(id=self.args[0])

            application.data = None

            application.variants.clear()

            for index, variant_id in enumerate(request.GET.getlist('variants', [])):
                try:
                    variant = Variant.objects.get(id=variant_id)

                    ApplicationVariantLink.objects.create(application=application, variant=variant, order=index)
                except Variant.DoesNotExist:
                    pass

            application.save()

            return redirect('wl_applications:check_identification')

        categories = []

        def __get_variants(variant_group, licence_type, current_params):
            variants = []

            for variant in variant_group.variants.all():
                variant_dict = {'text': variant.name}

                params = current_params + [variant]

                if variant_group.child is not None:
                    variant_dict['nodes'] = __get_variants(variant_group.child, licence_type, params)
                else:
                    encoded_params = urlencode({'variants': [v.id for v in params]}, doseq=True)

                    variant_dict['href'] = '{}?{}'.format(reverse('wl_applications:select_licence_type',
                                                                  args=(licence_type.id,)), encoded_params)

                    prod_code = '{} {}'.format(licence_type.product_title, ' '.join([v.product_title for v in params]))
                    variant_dict['price'] = get_licence_price(prod_code)

                variant_dict['help_text'] = variant.help_text

                variants.append(variant_dict)

            return variants

        def __populate_category_dict(category_dict, licence_type_queryset, categories):
            for licence_type in licence_type_queryset:
                licence_type_dict = {'text': licence_type.name}

                if licence_type.variant_group is not None:
                    licence_type_dict['nodes'] = __get_variants(licence_type.variant_group, licence_type, [])
                else:
                    licence_type_dict['href'] = reverse('wl_applications:select_licence_type',
                                                        args=(licence_type.id,))

                    licence_type_dict['price'] = get_licence_price(licence_type.product_title)

                category_dict['licence_types'].append(licence_type_dict)

                licence_type_dict['help_text'] = licence_type.help_text

            categories.append(category_dict)

        for category in WildlifeLicenceCategory.objects.all():
            __populate_category_dict({'name': category.name, 'licence_types': []},
                                     WildlifeLicenceType.objects.filter(category=category, replaced_by__isnull=True).exclude(effective_to__lte=datetime.now()),
                                     categories)

        uncategorised_queryset = WildlifeLicenceType.objects.filter(category__isnull=True, replaced_by__isnull=True).exclude(effective_to__lte=datetime.now())
        if uncategorised_queryset.exists():
            __populate_category_dict({'name': 'Other', 'licence_types': []}, uncategorised_queryset, categories)

        return render(request, self.template_name, {
            'application': application,
            'categories': categories
        })


class CheckIdentificationRequiredView(LoginRequiredMixin, ApplicationEntryBaseView, FormView):
    template_name = 'wl/entry/upload_identification.html'
    form_class = IdentificationForm

    def get(self, *args, **kwargs):
        application = utils.get_session_application(self.request.session)

        if application.licence_type.identification_required and application.applicant.identification is None:
            return super(CheckIdentificationRequiredView, self).get(*args, **kwargs)
        else:
            return redirect('wl_applications:check_senior_card')

    def get_context_data(self, **kwargs):
        application = utils.get_session_application(self.request.session)

        kwargs['application'] = application

        kwargs['file_types'] = ', '.join(['.' + file_ext for file_ext in IdentificationForm.VALID_FILE_TYPES])

        return super(CheckIdentificationRequiredView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        application = utils.get_session_application(self.request.session)

        if application.applicant.identification is not None:
            application.applicant.identification.delete()

        application.applicant.identification = Document.objects.create(file=self.request.FILES['identification_file'])
        application.applicant.save()

        # update any other applications for this user that are awaiting ID upload
        for app in Application.objects.filter(applicant=application.applicant):
            if app.id_check_status == 'awaiting_update':
                app.id_check_status = 'updated'
                app.save()

        return redirect('wl_applications:check_senior_card')


class CheckSeniorCardView(LoginRequiredMixin, ApplicationEntryBaseView, FormView):
    template_name = 'wl/entry/upload_senior_card.html'
    form_class = SeniorCardForm

    def get(self, *args, **kwargs):
        application = utils.get_session_application(self.request.session)

        if application.licence_type.senior_applicable \
                and application.applicant.is_senior \
                and application.applicant.senior_card is None:
            return super(CheckSeniorCardView, self).get(*args, **kwargs)
        else:
            return redirect('wl_applications:create_select_profile')

    def get_context_data(self, **kwargs):
        kwargs['application'] = utils.get_session_application(self.request.session)

        kwargs['file_types'] = ', '.join(['.' + file_ext for file_ext in self.form_class.VALID_FILE_TYPES])
        return super(CheckSeniorCardView, self).get_context_data(**kwargs)

    def form_valid(self, form):
        application = utils.get_session_application(self.request.session)

        if application.applicant.senior_card is not None:
            application.applicant.senior_card.delete()

        application.applicant.senior_card = Document.objects.create(file=self.request.FILES['senior_card'])
        application.applicant.save()

        return redirect('wl_applications:create_select_profile')


class CreateSelectProfileView(LoginRequiredMixin, ApplicationEntryBaseView):
    template_name = 'wl/entry/create_select_profile.html'

    def get_context_data(self, **kwargs):
        application = utils.get_session_application(self.request.session)

        kwargs['application'] = application

        profile_exists = application.applicant.profiles.count() > 0

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

        kwargs['address_form'] = AddressForm(user=application.applicant)

        return super(CreateSelectProfileView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        application = utils.get_session_application(request.session)

        if 'select' in request.POST:
            profile_selection_form = ProfileSelectionForm(request.POST, user=application.applicant)

            if profile_selection_form.is_valid():
                application.applicant_profile = profile_selection_form.cleaned_data.get('profile')
                application.save()
            else:
                return render(request, self.template_name, {'application': application,
                                                            'profile_selection_form': profile_selection_form,
                                                            'profile_creation_form': ProfileForm(),
                                                            'address_form': AddressForm(user=application.applicant)})
        elif 'create' in request.POST:
            profile_form = ProfileForm(request.POST)
            address_form = AddressForm(request.POST)

            if profile_form.is_valid() and address_form.is_valid():
                profile = profile_form.save(commit=False)
                profile.postal_address = address_form.save()
                profile.save()

                application.applicant_profile = profile
                application.save()
                application.log_user_action(
                    ApplicationUserAction.ACTION_CREATE_PROFILE_.format(profile),
                    request
                )
            else:
                return render(request, self.template_name,
                              {'application': application,
                               'licence_type': application.licence_type,
                               'profile_selection_form': ProfileSelectionForm(user=request.user),
                               'profile_creation_form': profile_form, 'address_form': address_form})

        return redirect('wl_applications:enter_details')


class EnterDetailsView(UserCanEditApplicationMixin, ApplicationEntryBaseView):
    template_name = 'wl/entry/enter_details.html'

    def get_context_data(self, **kwargs):
        application = utils.get_session_application(self.request.session)

        if application.review_status == 'awaiting_amendments':
            amendments = AmendmentRequest.objects.filter(application=application).filter(status='requested')
            kwargs['amendments'] = amendments

        if application.data:
            utils.convert_documents_to_url(application.data, application.documents.all(), '')

        kwargs['application'] = application

        return super(EnterDetailsView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        application = utils.get_session_application(self.request.session)

        application.data = utils.create_data_from_form(application.licence_type.application_schema,
                                                       request.POST, request.FILES)

        for f in request.FILES:
            if f == 'application_document':
                if application.hard_copy is None:
                    application.hard_copy = Document.objects.create(name='hard_copy')
                application.hard_copy.file = request.FILES[f]
                application.hard_copy.save()
            else:
                document = Document.objects.create(name=f, file=request.FILES[f])
                document.save()
                # for legacy applications, need to check if there's a document where file is
                # named by the file name rather than the form field name
                try:
                    old_document = application.documents.get(name=str(request.FILES[f]))
                except Document.DoesNotExist:
                    old_document = application.documents.filter(name=f).first()

                if old_document is not None:
                    application.documents.remove(old_document)

                application.documents.add(document)

        application.save()

        if 'draft' in request.POST or 'draft_continue' in request.POST:
            application.customer_status = 'draft'

            # The processing status should only be set to 'draft' if the application hasn't been lodged
            if not application.lodgement_number:
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
        application = utils.get_session_application(self.request.session)

        kwargs['is_payment_required'] = not is_licence_free(generate_product_title(application)) and \
            not application.invoice_reference and is_customer(self.request.user)

        if application.data:
            utils.convert_documents_to_url(application.data, application.documents.all(), '')

        if application.hard_copy is not None:
            application.licence_type.application_schema, application.data = utils.\
                append_app_document_to_schema_data(application.licence_type.application_schema, application.data,
                                                   application.hard_copy.file.url)
        else:
            kwargs['data'] = application.data

        kwargs['application'] = application

        return super(PreviewView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        application = utils.get_session_application(self.request.session)

        application.correctness_disclaimer = request.POST.get('correctnessDisclaimer', '') == 'on'
        application.further_information_disclaimer = request.POST.get('furtherInfoDisclaimer', '') == 'on'

        application.save()

        if application.invoice_reference:
            return redirect('wl_applications:complete')
        else:
            return redirect(reverse('wl_payments:checkout_application', args=[application.pk]))


class ApplicationCompleteView(UserCanViewApplicationMixin, ApplicationEntryBaseView):
    template_name = 'wl/entry/complete.html'

    def get(self, request, *args, **kwargs):
        application = utils.get_session_application(self.request.session)

        application.lodgement_sequence += 1
        application.lodgement_date = datetime.now().date()

        if application.customer_status == 'amendment_required':
            # this is a 're-lodged' application after some amendment were required.
            # from this point we assume that all the amendments have been amended.
            AmendmentRequest.objects.filter(application=application).filter(status='requested').update(status='amended')
            application.review_status = 'amended'
            application.processing_status = 'ready_for_action'
        else :
            application.processing_status = 'new'

        application.customer_status = 'under_review'

        if not application.lodgement_number:
            application.lodgement_number = '%s-%s' % (str(application.licence_type.pk).zfill(LICENCE_TYPE_NUM_CHARS),
                                                      str(application.pk).zfill(LODGEMENT_NUMBER_NUM_CHARS))

        application.log_user_action(
            ApplicationUserAction.ACTION_LODGE_APPLICATION.format(application),
            request
        )
        # update invoice reference if received, else keep the same
        application.invoice_reference = request.GET.get('invoice', application.invoice_reference)

        application.save(version_user=application.applicant, version_comment='Details Modified')

        context = {}

        context['application'] = application

        context['show_invoice'] = not is_licence_free(generate_product_title(application)) and \
            not application.application_type == 'amendment'

        delete_session_application(request.session)

        return render(request, self.template_name, context)
