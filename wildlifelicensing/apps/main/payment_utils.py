import requests
import json

from django.views.generic.base import RedirectView
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.http import urlencode

from oscar.apps.partner.strategy import Selector

from ledger.payments.utils import createBasket
from ledger.catalogue.models import Product
from ledger.payments.invoice.models import Invoice

from wildlifelicensing.apps.applications.models import Application
from ledger.settings import LEDGER_PASS

PAYMENT_SYSTEM_ID = 'S369'

PAYMENT_STATUS_PAID = 'paid'
PAYMENT_STATUS_CC_READY = 'cc_ready'
PAYMENT_STATUS_AWAITING = 'awaiting'
PAYMENT_STATUS_NOT_REQUIRED = 'not_required'

PAYMENT_STATUSES = {
    PAYMENT_STATUS_PAID: 'Paid',
    PAYMENT_STATUS_CC_READY: 'Credit Card Ready',
    PAYMENT_STATUS_AWAITING: 'Awaiting Manual Payment',
    PAYMENT_STATUS_NOT_REQUIRED: 'Not Required',
}


def application_requires_payment(application):
    return licence_requires_payment(application.licence_type)


def licence_requires_payment(licence_type):
    try:
        product = Product.objects.get(title=licence_type.code_slug)

        selector = Selector()
        strategy = selector.strategy()
        purchase_info = strategy.fetch_for_product(product=product)

        return purchase_info.price.excl_tax > 0

    except Product.DoesNotExist:
        return False


class CheckoutApplicationView(RedirectView):
    def get(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=args[0])
        product = get_product(application)
        user = application.applicant_profile.user.id

        error_url = request.build_absolute_uri(reverse('wl_applications:preview', args=(application.licence_type.code_slug, application.id,)))
        success_url = request.build_absolute_uri(reverse('wl_applications:complete', args=(application.licence_type.code_slug, application.id,)))

        parameters = {
            'system': PAYMENT_SYSTEM_ID,
            'basket_owner': user,
            'associateInvoiceWithToken': True,
            'checkoutWithToken': True,
            'fallback_url': error_url,
            'return_url': success_url,
            'forceRedirect': True,
            'products': [
                {"id": product.id}
            ]
        }

        url = request.build_absolute_uri(
            reverse('payments:ledger-initial-checkout')
        )

        response = requests.post(url, cookies=request.COOKIES, data=parameters)

        print response.content

        return HttpResponse(response.content)


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
    invoice = get_object_or_404(Invoice, reference=application.invoice_number)

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


class InitiatePayment(RedirectView):
    # TODO: implementation
    def get(self, *args, **kwargs):
        raise NotImplementedError


class ManualPaymentView(RedirectView):
    def get(self, *args, **kwargs):
        raise NotImplementedError

# if is_application_paid -> issue licence
# else:
#   if is_reserved_payment_approved(app):
#       redirect to InitiatePayment (application)
#   if is_manual:
#       redirect to manual page.
