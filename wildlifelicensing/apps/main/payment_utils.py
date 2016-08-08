import json

from django.views.generic.base import RedirectView
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.http import urlencode

from oscar.apps.partner.strategy import Selector

from ledger.payments.utils import createBasket
from ledger.catalogue.models import Product

SYSTEM_ID = '0369'


def licence_requires_payment(licence_type):
    try:
        product = Product.objects.get(title=licence_type.code_slug)

        selector = Selector()
        strategy = selector.strategy()
        purchase_info = strategy.fetch_for_product(product=product)

        return purchase_info.price.excl_tax > 0

    except Product.DoesNotExist:
        return False


class CheckoutView(RedirectView):
    def get(self, *args, **kwargs):
        product = get_object_or_404(Product, title=self.request.GET.get('product_name'))

        products_json = [{
            "id": product.id,
            "quantity": 1
        }]

        createBasket(json.dumps(products_json), self.request.user, SYSTEM_ID)

        url_query_parameters = {
            'system_id': SYSTEM_ID,
            'basket_owner': self.request.GET.get('user', self.request.user),
            'checkoutWithToken': True,
            'fallback_url': self.request.GET.get('fallback_url'),
            'return_url': self.request.GET.get('return_url')
        }

        url = '{}?{}'.format(reverse('checkout:index'), urlencode(url_query_parameters))

        return redirect(url)


def is_application_paid(application):
    raise NotImplementedError


class InitiatePayment(RedirectView):
    raise NotImplementedError
