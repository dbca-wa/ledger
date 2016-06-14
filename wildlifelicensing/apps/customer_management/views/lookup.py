from django.contrib import messages
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect, get_object_or_404

from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.signals import identification_uploaded
from wildlifelicensing.apps.customer_management.forms import CustomerSearchForm, CustomerDetailsForm

from ledger.accounts.models import EmailUser, Profile, Document
from ledger.accounts.forms import ProfileForm, AddressForm


class CustomerLookupView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/customer_lookup.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        kwargs['form'] = CustomerSearchForm()

        return super(CustomerLookupView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        form = CustomerSearchForm(request.POST)

        if form.is_valid():
            search = form.cleaned_data.get('search')
            if ' ' in search:
                if ',' in search:
                    last_name, first_name = search.split(',', 1)
                else:
                    first_name, last_name = search.split(None, 1)
            else:
                first_name = ''
                last_name = search

            first_name = first_name.strip()
            last_name = last_name.strip()

        customers = EmailUser.objects.filter(first_name__istartswith=first_name, last_name__istartswith=last_name, groups=None)

        return render(request, self.template_name, {'form': form, 'customers': customers})


class ViewCustomerView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/view_customer.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        kwargs['customer'] = get_object_or_404(EmailUser, pk=self.args[0])

        return super(ViewCustomerView, self).get_context_data(**kwargs)


class EditDetailsView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/officer_edit_customer_details.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        customer = get_object_or_404(EmailUser, pk=self.args[0])
        kwargs['customer'] = customer
        kwargs['form'] = CustomerDetailsForm(instance=customer)

        return super(EditDetailsView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        customer = get_object_or_404(EmailUser, pk=self.args[0])

        emailuser_form = CustomerDetailsForm(request.POST, instance=customer)

        if emailuser_form.is_valid():
            emailuser_form.save()

            if customer.identification is not None:
                customer.identification.delete()

            customer.identification = Document.objects.create(file=self.request.FILES['identification'])
            customer.save()

            identification_uploaded.send(sender=self.__class__, user=self.request.user)
        else:
            return render(request, self.template_name, {'customer': customer,
                                                        'form': emailuser_form})

        messages.success(request, 'The details were updated.')

        return redirect('customer_management:view_customer', customer.pk)


class EditProfileView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/officer_edit_customer_profile.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        kwargs['customer'] = get_object_or_404(EmailUser, pk=self.args[0])

        if len(self.args) > 1:
            profile = get_object_or_404(Profile, pk=self.args[1])
            kwargs['profile_form'] = ProfileForm(instance=profile)
            kwargs['address_form'] = AddressForm(instance=profile.postal_address)
        else:
            kwargs['profile_form'] = ProfileForm()
            kwargs['address_form'] = AddressForm()

        return super(EditProfileView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        customer = get_object_or_404(EmailUser, pk=self.args[0])

        if len(self.args) > 1:
            profile = get_object_or_404(Profile, pk=args[0])
            profile_form = ProfileForm(request.POST, instance=profile)
            address_form = AddressForm(request.POST, instance=profile.postal_address)
        else:
            profile_form = ProfileForm(request.POST)
            address_form = AddressForm(request.POST)

        if profile_form.is_valid() and address_form.is_valid():
            profile = profile_form.save(commit=False)
            address = address_form.save()
            profile.user = customer
            profile.postal_address = address
            profile.save()
        else:
            return render(request, self.template_name, {'customer': customer,
                                                        'profile_form': profile_form,
                                                        'address_form': address_form})

        messages.success(request, "The profile '%s' was updated." % profile.name)

        return redirect('customer_management:view_customer', profile.user.pk)
