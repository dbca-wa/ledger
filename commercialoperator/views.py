from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.decorators.csrf import csrf_protect

from datetime import datetime, timedelta

from commercialoperator.helpers import is_internal
from commercialoperator.forms import *
from commercialoperator.components.proposals.models import Referral, Proposal, HelpPage
from commercialoperator.components.compliances.models import Compliance
from commercialoperator.components.proposals.mixins import ReferralOwnerMixin
from commercialoperator.components.main.models import Park
from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission, get_cookie_basket
from django.core.management import call_command
import json
from decimal import Decimal

import logging
logger = logging.getLogger('payment_checkout')


class InternalView(UserPassesTestMixin, TemplateView):
    template_name = 'commercialoperator/dash/index.html'

    def test_func(self):
        return is_internal(self.request)

    def get_context_data(self, **kwargs):
        context = super(InternalView, self).get_context_data(**kwargs)
        context['dev'] = settings.DEV_STATIC
        context['dev_url'] = settings.DEV_STATIC_URL
        return context

class ExternalView(LoginRequiredMixin, TemplateView):
    template_name = 'commercialoperator/dash/index.html'

    def get_context_data(self, **kwargs):
        context = super(ExternalView, self).get_context_data(**kwargs)
        context['dev'] = settings.DEV_STATIC
        context['dev_url'] = settings.DEV_STATIC_URL
        return context

class ReferralView(ReferralOwnerMixin, DetailView):
    model = Referral
    template_name = 'commercialoperator/dash/index.html'

class ExternalProposalView(DetailView):
    model = Proposal
    template_name = 'commercialoperator/dash/index.html'

class ExternalComplianceView(DetailView):
    model = Compliance
    template_name = 'commercialoperator/dash/index.html'

class InternalComplianceView(DetailView):
    model = Compliance
    template_name = 'commercialoperator/dash/index.html'

class CommercialOperatorRoutingView(TemplateView):
    template_name = 'commercialoperator/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_internal(self.request):
                return redirect('internal')
            return redirect('external')
        kwargs['form'] = LoginForm
        return super(CommercialOperatorRoutingView, self).get(*args, **kwargs)

class CommercialOperatorContactView(TemplateView):
    template_name = 'commercialoperator/contact.html'

class CommercialOperatorFurtherInformationView(TemplateView):
    template_name = 'commercialoperator/further_info.html'

class InternalProposalView(DetailView):
    #template_name = 'commercialoperator/index.html'
    model = Proposal
    template_name = 'commercialoperator/dash/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_internal(self.request):
                #return redirect('internal-proposal-detail')
                return super(InternalProposalView, self).get(*args, **kwargs)
            return redirect('external-proposal-detail')
        kwargs['form'] = LoginForm
        return super(CommercialOperatorRoutingDetailView, self).get(*args, **kwargs)


@login_required(login_url='ds_home')
def first_time(request):
    context = {}
    if request.method == 'POST':
        form = FirstTimeForm(request.POST)
        redirect_url = form.data['redirect_url']
        if not redirect_url:
            redirect_url = '/'
        if form.is_valid():
            # set user attributes
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.dob = form.cleaned_data['dob']
            request.user.save()
            return redirect(redirect_url)
        context['form'] = form
        context['redirect_url'] = redirect_url
        return render(request, 'commercialoperator/user_profile.html', context)
    # GET default
    if 'next' in request.GET:
        context['redirect_url'] = request.GET['next']
    else:
        context['redirect_url'] = '/'
    context['dev'] = settings.DEV_STATIC
    context['dev_url'] = settings.DEV_STATIC_URL
    #return render(request, 'commercialoperator/user_profile.html', context)
    return render(request, 'commercialoperator/dash/index.html', context)


class HelpView(LoginRequiredMixin, TemplateView):
    template_name = 'commercialoperator/help.html'

    def get_context_data(self, **kwargs):
        context = super(HelpView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            application_type = kwargs.get('application_type', None) 
            if kwargs.get('help_type', None)=='assessor':
                if is_internal(self.request):
                    qs = HelpPage.objects.filter(application_type__name__icontains=application_type, help_type=HelpPage.HELP_TEXT_INTERNAL).order_by('-version')
                    context['help'] = qs.first()
#                else:
#                    return TemplateResponse(self.request, 'commercialoperator/not-permitted.html', context)
#                    context['permitted'] = False
            else:
                qs = HelpPage.objects.filter(application_type__name__icontains=application_type, help_type=HelpPage.HELP_TEXT_EXTERNAL).order_by('-version')
                context['help'] = qs.first()
        return context


class ManagementCommandsView(LoginRequiredMixin, TemplateView):
    template_name = 'commercialoperator/mgt-commands.html'

    def post(self, request):
        data = {}
        command_script = request.POST.get('script', None)
        if command_script:
            print 'running {}'.format(command_script)
            call_command(command_script)
            data.update({command_script: 'true'})

        return render(request, self.template_name, data)

class MakePaymentView(TemplateView):
    #template_name = 'mooring/booking/make_booking.html'
    template_name = 'commercialoperator/mgt-commands.html'

    @csrf_protect
    def post(self, request, *args, **kwargs):
        import ipdb; ipdb.set_trace()

        proposal = Proposal.objects.get(id=kwargs['proposal_pk'])
        lines = self.create_lines(request)
        response = self.checkout(request, proposal, lines, invoice_text='Some invoice text')

        logger.info('{} built payment line items {} and handing over to payment gateway'.format('User {} with id {}'.format(proposal.submitter.get_full_name(),proposal.submitter.id), proposal.id))
        import ipdb; ipdb.set_trace()
        return response

    @csrf_protect
    def create_lines(self, request, invoice_text=None, vouchers=[], internal=False):
        """ Create the ledger lines - line items for invoice sent to payment system """

        lines = []
        tbody = json.loads(request.POST['tbody'])
        for row in tbody:
            park_id = row[0]['value']
            arrival = row[1]
            no_adults = int(row[2]) if row[2] else 0
            no_children = int(row[3]) if row[3] else 0
            park= Park.objects.get(id=park_id)
            #ledger_description = arrival + '. ' + park.name + ' (' + row[2] + ' Adults' + ')'
            oracle_code = 'ABC123 GST'
            #price_incl_tax = str(park.adult * int(no_adults))
            quantity = 1

            if no_adults > 0:
                lines.append(dict(
                    ledger_description = arrival + '. ' + park.name + ' (' + str(no_adults) + ' Adults' + ')',
                    oracle_code = 'ABC123 GST',
                    price_incl_tax = Decimal(park.adult * no_adults),
                    quantity = 1
                ))
                print arrival + '. ' + park.name + '. Adults: ' + str(no_adults) + ', Price: ' + str(park.adult * no_adults)

            if no_children > 0:

                lines.append(dict(
                    ledger_description = arrival + '. ' + park.name + ' (' + str(no_children) + ' Children' + ')',
                    oracle_code = 'ABC123 GST',
                    price_incl_tax = Decimal(park.child * no_children),
                    quantity = 1
                ))
                print arrival + '. ' + park.name + '. Children: ' + str(no_children) + ', Price: ' + str(park.child * no_children)

        return lines

    @csrf_protect
    def checkout(self, request, proposal, lines, invoice_text=None, vouchers=[], internal=False):
        #import ipdb; ipdb.set_trace()
        basket_params = {
            'products': lines,
            'vouchers': vouchers,
            'system': settings.PS_PAYMENT_SYSTEM_ID,
            'custom_basket': True,
        }

        basket, basket_hash = create_basket_session(request, basket_params)
        fallback_url = request.build_absolute_uri('/')
        checkout_params = {
            'system': settings.PS_PAYMENT_SYSTEM_ID,
            #'fallback_url': request.build_absolute_uri('/'),                                      # 'http://mooring-ria-jm.dbca.wa.gov.au/'
            #'return_url': request.build_absolute_uri(reverse('public_booking_success')),          # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
            #'return_preload_url': request.build_absolute_uri(reverse('public_booking_success')),  # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
            'fallback_url': fallback_url,
            'return_url': fallback_url + '/success/',
            'return_preload_url': fallback_url + '/success/',
            'force_redirect': True,
            'proxy': True if internal else False,
            'invoice_text': invoice_text,                                                         # 'Reservation for Jawaid Mushtaq from 2019-05-17 to 2019-05-19 at RIA 005'
        }
#    if not internal:
#        checkout_params['check_url'] = request.build_absolute_uri('/api/booking/{}/booking_checkout_status.json'.format(booking.id))
        if internal or request.user.is_anonymous():
            #checkout_params['basket_owner'] = booking.customer.id
            checkout_params['basket_owner'] = proposal.submitter_id


        create_checkout_session(request, checkout_params)

#    if internal:
#        response = place_order_submission(request)
#    else:
        response = HttpResponseRedirect(reverse('checkout:index'))
        # inject the current basket into the redirect response cookies
        # or else, anonymous users will be directionless
        response.set_cookie(
                settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
                max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
                secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
        )

#    if booking.cost_total < 0:
#        response = HttpResponseRedirect('/refund-payment')
#        response.set_cookie(
#            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
#            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
#            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
#        )
#
#    # Zero booking costs
#    if booking.cost_total < 1 and booking.cost_total > -1:
#        response = HttpResponseRedirect('/no-payment')
#        response.set_cookie(
#            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
#            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
#            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
#        )

        return response

