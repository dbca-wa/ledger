from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse,HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from preserialize.serialize import serialize

from ledger.accounts.models import Profile, Document,EmailIdentity,EmailUser,Address
from ledger.accounts.forms import AddressForm, ProfileForm,EmailUserForm,DocumentForm
from ledger.accounts.signals import name_changed

from forms import IdentificationForm
from mixins import CustomerRequiredMixin
from signals import identification_uploaded


class ListProfilesView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/list_profiles.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ListProfilesView, self).get_context_data(**kwargs)

        def posthook(instance,attr):
            attr["auth_identity"] = instance.auth_identity
            return attr

        #context['data'] = serialize(Profile.objects.filter(user=self.request.user),posthook=posthook)
        context['data'] = serialize(Profile.objects.filter(user=self.request.user))

        return context


class CreateProfilesView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/create_profile.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'profile_form': ProfileForm(),
                                                    'address_form': AddressForm()})

    def post(self, request, *args, **kwargs):
        profile_form = ProfileForm(request.POST)
        address_form = AddressForm(request.POST)

        if profile_form.is_valid() and address_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.postal_address = address_form.save()
            profile.user = request.user
            profile.save()
            #maintain email identity
            email = profile.email
            auth_identity = profile_form.cleaned_data.get("auth_identity",False)
            if auth_identity and email:
                identity, created = EmailIdentity.objects.get_or_create(email=email, user=profile.user)

        else:
            return render(request, self.template_name, {'profile_form': profile_form,
                                                        'address_form': address_form})

        messages.success(request, "The profile '%s' was created." % profile.name)

        return redirect('main:list_profiles')


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

        if profile.user != request.user:
            return HttpResponse('Unauthorized', status=401)
        origin_email = profile.email
        origin_auth_identity = profile.auth_identity
        profile_form = ProfileForm(request.POST, instance=profile)
        address_form = AddressForm(request.POST, instance=profile.postal_address)

        if profile_form.is_valid() and address_form.is_valid():
            profile.save()
            address_form.save()
            email = profile.email
            #maintain email identity
            auth_identity = profile_form.cleaned_data.get("auth_identity",False)
            if origin_email != email:
                if origin_auth_identity:
                    #user changed the profile's email, remove the email from EmailIdentity.
                    EmailIdentity.objects.filter(user=profile.user,email=origin_email).delete()
                if auth_identity and email:
                    identity, created = EmailIdentity.objects.get_or_create(email=email, user=profile.user)
            elif origin_auth_identity != auth_identity and email:
                if auth_identity:
                    identity, created = EmailIdentity.objects.get_or_create(email=email, user=profile.user)
                else:
                    EmailIdentity.objects.filter(user=profile.user,email=origin_email).delete()
        else:
            return render(request, self.template_name, {'profile_form': ProfileForm(instance=profile),
                                                        'address_form': AddressForm(instance=profile.postal_address)})

        messages.success(request, "The profile '%s' was updated." % profile.name)

        return redirect('main:list_profiles')


class IdentificationView(LoginRequiredMixin, FormView):
    template_name = 'wl/manage_identification.html'
    login_url = '/'
    form_class = IdentificationForm
    success_url = reverse_lazy('main:identification')

    def form_valid(self, form):
        if self.request.user.identification is not None:
            self.request.user.identification.delete()

        self.request.user.identification = Document.objects.create(file=self.request.FILES['identification_file'])
        self.request.user.save()

        identification_uploaded.send(sender=self.__class__, user=self.request.user)

        return super(IdentificationView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['file_types'] = ', '.join(['.' + file_ext for file_ext in IdentificationForm.VALID_FILE_TYPES])

        if self.request.user.identification is not None:
            kwargs['existing_id_image_url'] = self.request.user.identification.file.url

        return super(IdentificationView, self).get_context_data(**kwargs)


class EditAccountView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/edit_account.html'
    login_url = '/'
    identification_url = reverse_lazy('main:identification')

    def get(self, request, *args, **kwargs):
        emailuser = get_object_or_404(EmailUser, pk=request.user.id)
        #get address source type
        residential_address_source_type = "added" if emailuser.residential_address else "removed"
        postal_address_source_type =  "removed" if not emailuser.postal_address else ("residential_address" if emailuser.postal_address == emailuser.residential_address else "added")
        billing_address_source_type =  "removed" if not emailuser.billing_address else ("residential_address" if emailuser.billing_address == emailuser.residential_address else ("postal_address" if emailuser.billing_address == emailuser.postal_address else "added"))
 
        #if user doesn't choose a identification, display a warning message
        if not emailuser.identification:
            messages.warning(request, "Please update a identification.")

        return render(request, self.template_name, {'emailuser_form': EmailUserForm(instance=emailuser),
                                                    'residential_address_form': AddressForm(prefix="residential_address",instance=emailuser.residential_address),
                                                    'postal_address_form': AddressForm(prefix="postal_address",instance=emailuser.postal_address),
                                                    'billing_address_form': AddressForm(prefix="billing_address",instance=emailuser.billing_address),
                                                    'residential_address_source_type':residential_address_source_type,
                                                    'postal_address_source_type':postal_address_source_type,
                                                    'billing_address_source_type':billing_address_source_type,
                                                    })

    def post(self, request, *args, **kwargs):
        #validate request
        residential_address_source_type = request.POST.get("residential_address-source_type")
        if not residential_address_source_type:
            return HttpResponseBadRequest("Missing resiential address source type.")

        postal_address_source_type = request.POST.get("postal_address-source_type")
        if not postal_address_source_type:
            return HttpResponseBadRequest("Missing postal address source type.")

        billing_address_source_type = request.POST.get("billing_address-source_type")
        if not billing_address_source_type:
            return HttpResponseBadRequest("Missing billing address source type.")


        emailuser = get_object_or_404(EmailUser, pk=request.user.pk)
        #Save the original user data.
        original_first_name = emailuser.first_name
        original_last_name = emailuser.last_name
        #original_identification = emailuser.identification

        original_residential_address_source_type = "added" if emailuser.residential_address else "removed"
        original_postal_address_source_type =  "removed" if not emailuser.postal_address else ("residential_address" if emailuser.postal_address == emailuser.residential_address else "added")
        original_billing_address_source_type =  "removed" if not emailuser.billing_address else ("residential_address" if emailuser.billing_address == emailuser.residential_address else ("postal_address" if emailuser.billing_address == emailuser.postal_address else "added"))

        original_residential_address = emailuser.residential_address
        original_postal_address =  emailuser.postal_address
        original_billing_address =  emailuser.billing_address

        emailuser_form = EmailUserForm(request.POST,instance=emailuser)

        #populate address form to validate and save if required
        if residential_address_source_type == "added":
            residential_address_form = AddressForm(request.POST,prefix="residential_address",instance=emailuser.residential_address)
        else:
            residential_address_form = None

        if postal_address_source_type == "added":
            if original_postal_address_source_type == "added":
                postal_address_form = AddressForm(request.POST,prefix="postal_address",instance=emailuser.postal_address)
            else:
                postal_address_form = AddressForm(request.POST,prefix="postal_address")
        else:
            postal_address_form = None

        if billing_address_source_type == "added":
            if original_billing_address_source_type == "added":
                billing_address_form = AddressForm(request.POST,prefix="billing_address",instance=emailuser.billing_address)
            else:
                billing_address_form = AddressForm(request.POST,prefix="billing_address")
        else:
            billing_address_form = None

        if (emailuser_form.is_valid() and 
            (not residential_address_form or  residential_address_form.is_valid()) and
            (not postal_address_form or postal_address_form.is_valid()) and
            (not billing_address_form or billing_address_form.is_valid())
        ):
            emailuser = emailuser_form.save(commit=False)
            is_name_changed = any([original_first_name != emailuser.first_name,original_last_name != emailuser.last_name])

            if is_name_changed :
                #user need to update his/her identification
                emailuser.identification = None   
            #save user address information.

            if residential_address_source_type == "added":
                emailuser.residential_address = residential_address_form.save()
            else:
                emailuser.residential_address = None

            if postal_address_source_type == "added":
                emailuser.postal_address = postal_address_form.save()
            elif postal_address_source_type == "residential_address":
                emailuser.postal_address = emailuser.residential_address
            else:
                emailuser.postal_address = None

            if billing_address_source_type == "added":
                emailuser.billing_address = billing_address_form.save()
            elif billing_address_source_type == "residential_address":
                emailuser.billing_address = emailuser.residential_address
            elif billing_address_source_type == "postal_address":
                emailuser.billing_address = emailuser.postal_address
            else:
                emailuser.billing_address = None
            #save user info
            emailuser.save()

            #remove old address if required.
            if residential_address_source_type == "removed" and original_residential_address:
                original_residential_address.delete()

            if original_postal_address_source_type == "added" and postal_address_source_type != "added":
                original_postal_address.delete()
                            
            if original_billing_address_source_type == "added" and billing_address_source_type != "added":
                original_billing_address.delete()
                            
            #send signal if either first name or last name is changed
            if is_name_changed:
                name_changed.send(sender=self.__class__, user=emailuser)
                messages.warning(request, "Please upload a new identification after you changed your name.")
                return redirect(self.identification_url)
            elif not emailuser.identification:
                messages.warning(request, "Please update a identification.")
            else:
                messages.success(request, "User account was saved.")

        return render(request, self.template_name, {'emailuser_form': emailuser_form,
                                                    'residential_address_form': residential_address_form or AddressForm(prefix="residential_address"),
                                                    'postal_address_form': postal_address_form or AddressForm(prefix="postal_address"),
                                                    'billing_address_form': billing_address_form or AddressForm(prefix="billing_address"),
                                                    'residential_address_source_type':residential_address_source_type,
                                                    'postal_address_source_type':postal_address_source_type,
                                                    'billing_address_source_type':billing_address_source_type,
                                                    })


class ListDocumentView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/list_documents.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ListDocumentView, self).get_context_data(**kwargs)

        context['data'] = serialize(self.request.user.documents.all())

        return context


class CreateDocumentView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/create_document.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'document_form': DocumentForm()})

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(EmailUser, pk=request.user.id)

        document_form = DocumentForm(request.POST,request.FILES)

        if document_form.is_valid() :
            document = document_form.save()
            user.documents.add(document)
            messages.success(request, "The document '%s' was created." % document.name)
            return redirect('main:list_documents')
        else:
            return render(request, self.template_name, {'document_form': document_form})

class DeleteDocumentView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/list_documents.html'
    login_url = '/'

    def get(self,request,id, *args, **kwargs):
        document = get_object_or_404(Document, pk=id)
        document.delete()
        messages.success(request, "The document '%s' was deleted." % document.name)
        return redirect('main:list_documents')



class EditDocumentView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/edit_document.html'
    login_url = '/'

    def get(self, request,id, *args, **kwargs):
        document = get_object_or_404(Document, pk=id)
        return render(request, self.template_name, {'document_form': DocumentForm(instance=document)})

    def post(self, request,id, *args, **kwargs):
        document = get_object_or_404(Document, pk=id)
        document_form = DocumentForm(request.POST,request.FILES,instance=document)

        if document_form.is_valid() :
            document = document_form.save()
            messages.success(request, "The document '%s' was edited." % document.name)
            return redirect('main:list_documents')
        else:
            return render(request, self.template_name, {'document_form': document_form})



