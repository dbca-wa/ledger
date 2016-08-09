import json

from django.views.generic.base import RedirectView
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.http import urlencode

from oscar.apps.partner.strategy import Selector

from ledger.payments.utils import createBasket
from ledger.catalogue.models import Product

from wildlifelicensing.apps.applications.models import Application

PAYMENT_SYSTEM_ID = '0369'


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
    def get(self, *args, **kwargs):
        application = get_object_or_404(Application, pk=args[0])
        product = get_product_or_404(application)
        user = application.applicant_profile.user.id
        success_url = self.request.GET.get('return_url', reverse('wl_home'))
        error_url = self.request.GET.get('fallback_url', reverse('wl_home'))

        products = [{
            "id": product.id,
            "quantity": 1
        }]

        createBasket(products, self.request.user, PAYMENT_SYSTEM_ID)

        url_query_parameters = {
            'system_id': PAYMENT_SYSTEM_ID,
            'basket_owner': user,
            'checkoutWithToken': True,
            'fallback_url': error_url,
            'return_url': success_url
        }

        url = '{}?{}'.format(reverse('checkout:index'), urlencode(url_query_parameters))

        return redirect(url)


def get_product_title(application):
    return application.licence_type.code_slug


def get_product_or_404(application):
    return get_object_or_404(Product, title=get_product_title(application))


def is_reserved_payment_approved(application):
    raise NotImplementedError


def is_application_paid(application):
    # TODO: implementation
    raise NotImplementedError


def is_manual_payment(application):
    raise NotImplementedError


def get_application_payment_status(application):
    """

    :param application:
    :return: something like paid, reserved, awaiting, not required
    """
    raise NotImplementedError


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
