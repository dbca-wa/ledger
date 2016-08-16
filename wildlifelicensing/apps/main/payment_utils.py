import json

import requests
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.http import urlencode
from django.views.generic.base import RedirectView, View
from django import forms
from django.contrib import messages

from ledger.catalogue.models import Product
from ledger.payments.invoice.models import Invoice
from wildlifelicensing.apps.applications.models import Application

PAYMENT_SYSTEM_ID = 'S369'

PAYMENT_STATUS_PAID = 'paid'
PAYMENT_STATUS_CC_READY = 'cc_ready'
PAYMENT_STATUS_AWAITING = 'awaiting'
PAYMENT_STATUS_NOT_REQUIRED = 'not_required'

PAYMENT_STATUSES = {
    PAYMENT_STATUS_PAID: 'Paid',
    PAYMENT_STATUS_CC_READY: 'Credit Card Ready',
    PAYMENT_STATUS_AWAITING: 'Awaiting Payment',
    PAYMENT_STATUS_NOT_REQUIRED: 'Payment Not Required',
}

JSON_REQUEST_HEADER_PARAMS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}


def get_product(application):
    try:
        return Product.objects.get(title=application.licence_type.code_slug)
    except Product.DoesNotExist:
        return None


def get_application_payment_status(application):
    """

    :param application:
    :return: One of PAYMENT_STATUS_PAID, PAYMENT_STATUS_CC_READY, PAYMENT_STATUS_AWAITING or PAYMENT_STATUS_NOT_REQUIRED
    """
    if not application.invoice_reference:
        return PAYMENT_STATUS_NOT_REQUIRED

    invoice = get_object_or_404(Invoice, reference=application.invoice_reference)

    if invoice.amount > 0:
        payment_status = invoice.payment_status

        if payment_status == 'paid' or payment_status == 'over_paid':
            return PAYMENT_STATUS_PAID
        elif invoice.token:
            return PAYMENT_STATUS_CC_READY
        else:
            return PAYMENT_STATUS_AWAITING
    else:
        return PAYMENT_STATUS_NOT_REQUIRED


def invoke_credit_card_payment(application):
    invoice = get_object_or_404(Invoice, reference=application.invoice_reference)

    if not invoice.token:
        raise Exception('Application invoice does have a credit payment token')

    invoice.make_payment()


class CheckoutApplicationView(RedirectView):
    def get(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=args[0])
        product = get_product(application)
        user = application.applicant_profile.user.id

        error_url = request.build_absolute_uri(
            reverse('wl_applications:preview', args=(application.licence_type.code_slug, application.id,)))
        success_url = request.build_absolute_uri(
            reverse('wl_applications:complete', args=(application.licence_type.code_slug, application.id,)))

        parameters = {
            'system': PAYMENT_SYSTEM_ID,
            'basket_owner': user,
            'associateInvoiceWithToken': True,
            'checkoutWithToken': True,
            'fallback_url': error_url,
            'return_url': success_url,
            'forceRedirect': True,
            "products": [
                {"id": product.id}
            ]
        }

        url = request.build_absolute_uri(
            reverse('payments:ledger-initial-checkout')
        )

        response = requests.post(url, headers=JSON_REQUEST_HEADER_PARAMS, cookies=request.COOKIES,
                                 data=json.dumps(parameters))

        return HttpResponse(response.content)


class ManualPaymentView(RedirectView):
    def get(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=args[0])

        url = reverse('payments:invoice-payment', args=(application.invoice_reference,))

        params = {
            'redirect_url': request.GET.get('redirect_url', reverse('wl_home'))
        }

        return redirect('{}?{}'.format(url, urlencode(params)))


class PaymentsReportForm(forms.Form):
    start = forms.DateTimeField(required=True)
    end = forms.DateTimeField(required=True)

    def __init__(self, *args, **kwargs):
        super(PaymentsReportForm, self).__init__(*args, **kwargs)


class PaymentsReportView(View):
    def get(self, request):
        form = PaymentsReportForm(request.GET)
        if form.is_valid():
            start = form.cleaned_data.get('start')
            end = form.cleaned_data.get('end')
            url = request.build_absolute_uri(
                reverse('payments:ledger-report')
            )

            parameters = {
                "system": PAYMENT_SYSTEM_ID,
                "start": start,
                "end": end
            }

            response = requests.post(url,
                                     headers=JSON_REQUEST_HEADER_PARAMS,
                                     cookies=request.COOKIES,
                                     data=json.dumps(parameters))
            print('response', response.content)
            return HttpResponse(response.content)
        else:
            messages.error(request, form.errors)
            redirect('wl_reports:reports')
