import json
import requests

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import RedirectView, View
from django.utils.http import urlencode
from django.conf import settings
from django.utils import timezone

from ledger.checkout.utils import create_basket_session, create_checkout_session, place_order_submission

from wildlifelicensing.apps.applications.models import Application

from wildlifelicensing.apps.payments.utils import generate_product_title, get_product
from wildlifelicensing.apps.payments.forms import PaymentsReportForm
from wildlifelicensing.apps.main.helpers import is_officer


JSON_REQUEST_HEADER_PARAMS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

PAYMENT_SYSTEM_ID = settings.WL_PAYMENT_SYSTEM_ID

SENIOR_VOUCHER_CODE = settings.WL_SENIOR_VOUCHER_CODE


class CheckoutApplicationView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=args[0])
        product = get_product(generate_product_title(application))
        user = application.applicant.id

        error_url = request.build_absolute_uri(reverse('wl_applications:preview'))
        success_url = request.build_absolute_uri(reverse('wl_applications:complete'))

        basket_params = {
            'products': [
                {'id': product.id if product is not None else None}
            ],
            'vouchers': [],
            'system': PAYMENT_SYSTEM_ID
        }
        # senior discount
        if application.is_senior_offer_applicable:
            basket_params['vouchers'].append({'code': SENIOR_VOUCHER_CODE})
        basket, basket_hash = create_basket_session(request, basket_params)

        checkout_params = {
            'system': PAYMENT_SYSTEM_ID,
            'basket_owner': user,
            'associate_invoice_with_token': True,
            'fallback_url': error_url,
            'return_url': success_url,
            'force_redirect': True,
            'template': 'wl/payment_information.html',
            'proxy': is_officer(request.user),
        }
        create_checkout_session(request, checkout_params)

        if checkout_params['proxy']:
            response = place_order_submission(request)
        else:
            response = HttpResponseRedirect(reverse('checkout:index'))
        return response


class ManualPaymentView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=args[0])

        #url = reverse('payments:invoice-payment', args=(application.invoice_reference,))
        url = '{}?invoice={}'.format(reverse('payments:invoice-payment'),application.invoice_reference)
 
        params = {
            'redirect_url': request.GET.get('redirect_url', reverse('wl_home'))
        }
 
        return redirect('{}&{}'.format(url, urlencode(params)))


class PaymentsReportView(LoginRequiredMixin, View):
    success_url = reverse_lazy('wl_reports:reports')
    error_url = success_url

    def get(self, request):
        form = PaymentsReportForm(request.GET)
        if form.is_valid():
            start = form.cleaned_data.get('start')
            end = form.cleaned_data.get('end')
            banked_start = form.cleaned_data.get('banked_start')
            banked_end = form.cleaned_data.get('banked_end')
            # here start and end should be timezone aware (with the settings.TIME_ZONE
            start = timezone.make_aware(start) if not timezone.is_aware(start) else start
            end = timezone.make_aware(end) if not timezone.is_aware(end) else end
            banked_start = timezone.make_aware(banked_start) if not timezone.is_aware(banked_start) else banked_start
            banked_end = timezone.make_aware(banked_end) if not timezone.is_aware(banked_end) else banked_end

            url = request.build_absolute_uri(
                reverse('payments:ledger-report')
            )
            data = {
                'system': PAYMENT_SYSTEM_ID,
                'start': start,
                'end': end,
                'banked_start': banked_start,
                'banked_end': banked_end
            }
            if 'items' in request.GET:
                data['items'] = True
            response = requests.get(url,
                                    headers=JSON_REQUEST_HEADER_PARAMS,
                                    cookies=request.COOKIES,
                                    params=data,
                                    verify=False)
            if response.status_code == 200:
                filename = 'wl_payments-{}_{}'.format(
                    str(start.date()),
                    str(end.date())
                )
                response = HttpResponse(response, content_type='text/csv; charset=utf-8')
                response['Content-Disposition'] = 'attachment; filename={}.csv'.format(filename)
                return response
            else:
                messages.error(request,
                               "There was an error while generating the payment report:<br>{}".format(response.content))
                return redirect(self.error_url)
        else:
            messages.error(request, form.errors)
            return redirect(self.error_url)
