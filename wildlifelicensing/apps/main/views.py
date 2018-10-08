from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import View, TemplateView

from preserialize.serialize import serialize

from ledger.accounts.models import Profile, Document, EmailUser
from ledger.accounts.forms import AddressForm, ProfileForm, EmailUserForm

from wildlifelicensing.apps.main.models import CommunicationsLogEntry,\
    WildlifeLicence
from wildlifelicensing.apps.main.forms import IdentificationForm, CommunicationsLogEntryForm, SeniorCardForm
from wildlifelicensing.apps.main.mixins import CustomerRequiredMixin, OfficerRequiredMixin
from wildlifelicensing.apps.main.signals import identification_uploaded
from wildlifelicensing.apps.main.serializers import WildlifeLicensingJSONEncoder
from wildlifelicensing.apps.main.utils import format_communications_log_entry
from wildlifelicensing.apps.main.pdf import create_licence_renewal_pdf_bytes, bulk_licence_renewal_pdf_bytes
from wildlifelicensing.apps.applications.models import Application


class SearchCustomersView(OfficerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')

        if query is not None:
            q = (Q(first_name__icontains=query) | Q(last_name__icontains=query)) & Q(groups__isnull=True)
            qs = EmailUser.objects.filter(q)
        else:
            qs = EmailUser.objects.none()

        users = []
        for email_user in qs:
            users.append({
                'id': email_user.id,
                'text': email_user.get_full_name_dob() if email_user.dob is not None else email_user.get_full_name()
            })

        return JsonResponse(users, safe=False, encoder=WildlifeLicensingJSONEncoder)


class ListProfilesView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/list_profiles.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ListProfilesView, self).get_context_data(**kwargs)

        def posthook(instance, attr):
            attr["auth_identity"] = instance.auth_identity
            return attr

        #context['data'] = serialize(Profile.objects.filter(user=self.request.user))
        context['data'] = serialize(Profile.objects.filter(user=self.request.user),
                           related={
                               'user':{'exclude':['residential_address','postal_address','billing_address']},
                               'postal_address':{
                                   'related':{
                                       'oscar_address':{'exclude':['user']}
                                   },'exclude':['user']}
                           })

        return context


class CreateProfilesView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/create_profile.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'profile_form': ProfileForm(user=request.user),
                                                    'address_form': AddressForm(user=request.user)})

    def post(self, request, *args, **kwargs):
        if request.user.pk != int(request.POST['user']):
            return HttpResponse('Unauthorized', status=401)

        profile_form = ProfileForm(request.POST)
        address_form = AddressForm(request.POST)

        if profile_form.is_valid() and address_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.postal_address = address_form.save()
            profile.save()
        else:
            return render(request, self.template_name, {'profile_form': profile_form,
                                                        'address_form': address_form})

        messages.success(request, "The profile '%s' was created." % profile.name)

        return redirect('wl_main:list_profiles')


class DeleteProfileView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/list_profiles.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=args[0])
        profile.delete()
        messages.success(request, "The profile '%s' was deleted." % profile.name)
        return redirect('wl_main:list_profiles')


class EditProfilesView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/edit_profile.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=args[0])

        if profile.user != request.user:
            return HttpResponse('Unauthorized', status=401)

        return render(request, self.template_name, {'profile_form': ProfileForm(instance=profile),
                                                    'address_form': AddressForm(instance=profile.postal_address)})

    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=args[0])

        if profile.user != request.user or request.user.pk != int(request.POST['user']):
            return HttpResponse('Unauthorized', status=401)
        profile_form = ProfileForm(request.POST, instance=profile)
        address_form = AddressForm(request.POST, instance=profile.postal_address)

        if profile_form.is_valid() and address_form.is_valid():
            profile = profile_form.save()
            profile.postal_address = address_form.save()
            profile.save()
        else:
            return render(request, self.template_name, {'profile_form': profile_form,
                                                        'address_form': address_form})

        messages.success(request, "The profile '%s' was updated." % profile.name)

        return redirect('wl_main:list_profiles')


class IdentificationView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/manage_identification.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        if 'form_id' not in kwargs:
            kwargs['form_id'] = IdentificationForm()
        if self.request.user.identification:
            kwargs['existing_id_image_url'] = self.request.user.identification.file.url

        if self.request.user.is_senior:
            if 'form_senior' not in kwargs:
                kwargs['form_senior'] = SeniorCardForm()
            if self.request.user.senior_card:
                kwargs['existing_senior_card_image_url'] = self.request.user.senior_card.file.url

        if 'file_types' not in kwargs:
            kwargs['file_types'] = ', '.join(['.' + file_ext for file_ext in IdentificationForm.VALID_FILE_TYPES])
        return super(IdentificationView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        ctx = {}
        if 'identification' in request.POST:
            form = IdentificationForm(request.POST, files=request.FILES)
            ctx['form_id'] = form
            if form.is_valid():
                previous_id = self.request.user.identification
                self.request.user.identification = Document.objects.create(file=self.request.FILES['identification_file'])
                self.request.user.save()
                if bool(previous_id):
                    previous_id.delete()
                identification_uploaded.send(sender=self.__class__, request=self.request)
                
                messages.success(request, 'ID was successfully uploaded')
        if 'senior_card' in request.POST:
            form = SeniorCardForm(request.POST, files=request.FILES)
            ctx['form_senior'] = form
            if form.is_valid():
                previous_senior_card = self.request.user.senior_card
                self.request.user.senior_card = Document.objects.create(file=self.request.FILES['senior_card'])
                self.request.user.save()
                if bool(previous_senior_card):
                    previous_senior_card.delete()
                messages.success(request, 'Seniors card was successfully uploaded')

        return redirect('wl_home')


class EditAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/edit_account.html'
    login_url = '/'
    identification_url = reverse_lazy('wl_main:identification')

    def _process_discontinue(self, emailuser):
        # delete user but with a double-check security:
        # don't delete if there's any applications tied to this user
        if Application.objects.filter(applicant=emailuser).count() == 0:
            emailuser.delete()
        return redirect('wl_home')

    def get(self, request, *args, **kwargs):
        emailuser = get_object_or_404(EmailUser, pk=request.user.id)
        # if user doesn't choose a identification, display a warning message
        #if not emailuser.identification:
        #    messages.warning(request, "Please upload your identification.")

        return render(request, self.template_name, {'emailuser_form': EmailUserForm(instance=emailuser),})

    def post(self, request, *args, **kwargs):
        emailuser = get_object_or_404(EmailUser, pk=request.user.pk)
        new_user = not (emailuser.first_name or emailuser.last_name or emailuser.dob)
        if 'discontinue' in request.POST:
            return self._process_discontinue(emailuser)
        else:
            allow_discontinue = False
            # Save the original user data.
            original_first_name = emailuser.first_name
            original_last_name = emailuser.last_name
            emailuser_form = EmailUserForm(request.POST, instance=emailuser)
            if emailuser_form.is_valid():
                emailuser = emailuser_form.save(commit=False)
                # New user test case. Check the uniqueness of the user (first, last, dob).
                # https://kanboard.dpaw.wa.gov.au/?controller=TaskViewController&action=show&task_id=2994&project_id=24
                # TODO: This should be done at the ledger level !!!
                unique = EmailUser.objects.filter(
                    first_name=emailuser.first_name,
                    last_name=emailuser.last_name,
                    dob=emailuser.dob
                ).count() == 0
                emailuser.save()
                if new_user and not unique:
                    message = """This combination of given name(s), last name and date of birth is not unique.
                    If you already have a Parks and Wildlife customer account under another email address, please discontinue this registration and sign in with your existing account and add any additional email addresses as new profiles."""
                    messages.error(request, message)
                    allow_discontinue = True
                else:
                    is_name_changed = any([original_first_name != emailuser.first_name, original_last_name != emailuser.last_name])
                    # send signal if either first name or last name is changed
                    if is_name_changed:
                        messages.warning(request, "Please upload new identification after you changed your name.")
                        return redirect(self.identification_url)
                    else:
                        messages.success(request, "User account was saved.")
                        return redirect('wl_home')
            return render(request, self.template_name, {
                'emailuser_form': emailuser_form,
                'allow_discontinue': allow_discontinue
            })


class ListDocumentView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/list_documents.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ListDocumentView, self).get_context_data(**kwargs)

        context['data'] = serialize(self.request.user.documents.all())

        return context


class LicenceRenewalPDFView(OfficerRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        licence = get_object_or_404(WildlifeLicence, pk=self.args[0])

        filename = '{}-{}-renewal.pdf'.format(licence.licence_number, licence.licence_sequence)

        response = HttpResponse(content_type='application/pdf')

        response.write(create_licence_renewal_pdf_bytes(filename, licence,
                                                        request.build_absolute_uri(reverse('home'))))

        licence.renewal_sent = True
        licence.save()

        return response


class BulkLicenceRenewalPDFView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        query = request.POST.get('query')
        licences = []
        if query:
            licences = WildlifeLicence.objects.filter(query)
        filename = 'bulk-renewals.pdf'
        response = HttpResponse(content_type='application/pdf')
        response.write(bulk_licence_renewal_pdf_bytes(licences, request.build_absolute_uri(reverse('home'))))

        if licences:
            licences.update(renewal_sent=True)

        return response


class CommunicationsLogListView(OfficerRequiredMixin, View):
    serial_template = {
        'exclude': ['communicationslogentry_ptr', 'customer', 'staff'],
        'posthook': format_communications_log_entry
    }

    def get(self, request, *args, **kwargs):
        q = Q(staff=args[0]) | Q(customer=args[0])

        data = serialize(
            CommunicationsLogEntry.objects.filter(q).order_by('created'),
            **self.serial_template
        )

        return JsonResponse({'data': data}, safe=False, encoder=WildlifeLicensingJSONEncoder)


class AddCommunicationsLogEntryView(OfficerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        customer = get_object_or_404(EmailUser, pk=args[0])

        form = CommunicationsLogEntryForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            communications_log_entry = form.save(commit=False)

            communications_log_entry.customer = customer
            communications_log_entry.staff = request.user
            communications_log_entry.save()
            if request.FILES and 'attachment' in request.FILES:
                communications_log_entry.documents.add(Document.objects.create(file=request.FILES['attachment']))

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
