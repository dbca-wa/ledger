from django.contrib import messages
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse

from wildlifelicensing.apps.dashboard.views import base
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.signals import identification_uploaded
from wildlifelicensing.apps.customer_management.forms import CustomerDetailsForm

from ledger.accounts.models import EmailUser, Profile, Document
from ledger.accounts.forms import ProfileForm, AddressForm
from wildlifelicensing.apps.main.forms import CommunicationsLogEntryForm


class CustomerLookupView(OfficerRequiredMixin, base.TableBaseView):
    template_name = 'wl/customer_lookup.html'
    login_url = '/'

    def _build_data(self):
        data = super(CustomerLookupView, self)._build_data()

        # applications
        data['applications']['columnDefinitions'] = [
            {
                'title': 'Lodge Number'
            },
            {
                'title': 'Licence Type'
            },
            {
                'title': 'User'
            },
            {
                'title': 'Status',
            },
            {
                'title': 'Lodged on'
            },
            {
                'title': 'Assignee'
            },
            {
                'title': 'Proxy'
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]

        data['applications']['ajax']['url'] = reverse('wl_customer_management:data_applications', args=self.args)
        # global table options
        data['applications']['tableOptions'] = {
            'pageLength': 10
        }

        # licences
        data['licences']['columnDefinitions'] = [
            {
                'title': 'Licence Number'
            },
            {
                'title': 'Licence Type'
            },
            {
                'title': 'User'
            },
            {
                'title': 'Start Date'
            },
            {
                'title': 'Expiry Date'
            },
            {
                'title': 'Licence',
                'searchable': False,
                'orderable': False
            },
            {
                'title': 'Cover Letter',
                'searchable': False,
                'orderable': False
            },
            {
                'title': 'Renewal Letter',
                'searchable': False,
                'orderable': False
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['licences']['ajax']['url'] = reverse('wl_customer_management:data_licences', args=self.args)

        # global table options
        data['licences']['tableOptions'] = {
            'pageLength': 10
        }

        # returns
        data['returns']['columnDefinitions'] = [
            {
                'title': 'Lodge Number'
            },
            {
                'title': 'Licence Type'
            },
            {
                'title': 'User'
            },
            {
                'title': 'Lodged On'
            },
            {
                'title': 'Due On'
            },
            {
                'title': 'Status'
            },
            {
                'title': 'Licence',
                'orderable': False
            },
            {
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['returns']['ajax']['url'] = reverse('wl_customer_management:data_returns', args=self.args)
        # global table options
        data['returns']['tableOptions'] = {
            'pageLength': 10
        }

        return data

    def get(self, request, *args, **kwargs):
        if 'customer' in self.request.GET:
            customer = get_object_or_404(EmailUser, pk=self.request.GET.get('customer'))

            return redirect('wl_customer_management:customer_lookup', customer.pk)

        context = {}

        if len(self.args) > 0:
            customer = get_object_or_404(EmailUser, pk=self.args[0])

            kwargs['customer'] = customer

            kwargs['log_entry_form'] = CommunicationsLogEntryForm(to=customer.email, fromm=self.request.user.email)

            context = super(CustomerLookupView, self).get_context_data(**kwargs)

        return render(request, self.template_name, context)


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

            if 'identification' in self.request.FILES:
                if customer.identification is not None:
                    customer.identification.delete()

                customer.identification = Document.objects.create(file=self.request.FILES['identification'])
                customer.save()

                identification_uploaded.send(sender=self.__class__, user=self.request.user)
        else:
            return render(request, self.template_name, {'customer': customer,
                                                        'form': emailuser_form})

        messages.success(request, 'The details were updated. Please note that this may require any licences held by the user to be reissued.')

        return redirect('wl_customer_management:customer_lookup', customer.pk)


class EditProfileView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/officer_edit_customer_profile.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        customer = get_object_or_404(EmailUser, pk=self.args[0])

        kwargs['customer'] = customer

        if len(self.args) > 1:
            profile = get_object_or_404(Profile, pk=self.args[1])
            kwargs['profile_form'] = ProfileForm(instance=profile)
            kwargs['address_form'] = AddressForm(instance=profile.postal_address)
        else:
            kwargs['profile_form'] = ProfileForm(user=customer)
            kwargs['address_form'] = AddressForm()

        return super(EditProfileView, self).get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        customer = get_object_or_404(EmailUser, pk=self.args[0])

        if len(self.args) > 1:
            profile = get_object_or_404(Profile, pk=args[1])
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

        return redirect('wl_customer_management:customer_lookup', profile.user.pk)
