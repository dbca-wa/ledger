from django.contrib import messages
from django.views.generic.base import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse

from wildlifelicensing.apps.dashboard.views import base
from wildlifelicensing.apps.main.helpers import get_all_officers
from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin
from wildlifelicensing.apps.main.signals import identification_uploaded
from wildlifelicensing.apps.returns.models import Return
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


class ViewCustomerView(OfficerRequiredMixin, base.TableBaseView):
    template_name = 'wl/view_customer.html'
    login_url = '/'

    STATUS_PENDING = 'pending'

    STATUS_FILTER_ACTIVE = 'active'
    STATUS_FILTER_RENEWABLE = 'renewable'
    STATUS_FILTER_EXPIRED = 'expired'
    STATUS_FILTER_ALL = 'all'

    STATUS_FILTER_ALL_BUT_DRAFT_OR_FUTURE = 'all_but_draft_or_future'
    OVERDUE_FILTER = 'overdue'

    def _build_data(self):
        data = super(ViewCustomerView, self)._build_data()

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
        data['applications']['filters']['status']['values'] = \
            [('all', 'All')] + [(self.STATUS_PENDING, self.STATUS_PENDING.capitalize())] + \
            base.get_processing_statuses_but_draft()
        data['applications']['filters']['assignee'] = {
            'values': [('all', 'All')] + [(user.pk, base.render_user_name(user),) for user in get_all_officers()]
        }
        data['applications']['ajax']['url'] = reverse('wl_customer_management:data_applications', args=self.args)
        # global table options
        data['applications']['tableOptions'] = {
            'pageLength': 25
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
                'title': 'Action',
                'searchable': False,
                'orderable': False
            }
        ]
        data['licences']['ajax']['url'] = reverse('wl_customer_management:data_licences', args=self.args)
        # filters (note: there is already the licenceType from the super class)
        filters = {
            'status': {
                'values': [
                    (self.STATUS_FILTER_ACTIVE, self.STATUS_FILTER_ACTIVE.capitalize()),
                    (self.STATUS_FILTER_RENEWABLE, self.STATUS_FILTER_RENEWABLE.capitalize()),
                    (self.STATUS_FILTER_EXPIRED, self.STATUS_FILTER_EXPIRED.capitalize()),
                    (self.STATUS_FILTER_ALL, self.STATUS_FILTER_ALL.capitalize()),
                ]
            }
        }
        data['licences']['filters'].update(filters)
        # global table options
        data['licences']['tableOptions'] = {
            'pageLength': 25
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
            'pageLength': 25
        }
        filters = {
            'status': {
                'values': [
                    (self.STATUS_FILTER_ALL_BUT_DRAFT_OR_FUTURE, 'All (but draft or future)'),
                    (self.OVERDUE_FILTER, self.OVERDUE_FILTER.capitalize())
                ] + list(Return.STATUS_CHOICES)
            }
        }
        data['returns']['filters'].update(filters)

        return data

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

            if 'identification' in self.request.FILES:
                if customer.identification is not None:
                    customer.identification.delete()

                customer.identification = Document.objects.create(file=self.request.FILES['identification'])
                customer.save()

                identification_uploaded.send(sender=self.__class__, user=self.request.user)
        else:
            return render(request, self.template_name, {'customer': customer,
                                                        'form': emailuser_form})

        messages.success(request, 'The details were updated.')

        return redirect('wl_customer_management:view_customer', customer.pk)


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

        return redirect('wl_customer_management:view_customer', profile.user.pk)
