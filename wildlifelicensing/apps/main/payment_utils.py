import json

from django.views.generic.base import RedirectView
from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.http import urlencode

from ledger.payments.views import createBasket
from ledger.catalogue.models import Product


def licence_requires_payment(licence_type):
    raise NotImplementedError


class CheckoutView(RedirectView):
    def get(self, *args, **kwargs):
        product = get_object_or_404(Product, title=self.request.GET.get('product_name'))

        products_json = [{
            "id": product.id,
            "quantity": 1
        }]

        createBasket(json.dumps(products_json), self.request.user, '0369')

        url_query_parameters = {
            'system_id': '0369',
            'basket_owner': self.request.GET.get('user', self.request.user),
            'checkoutWithToken': True,
            'fallback_url': self.request.GET.get('fallback_url'),
            'return_url': self.request.GET.get('return_url')
        }

        url = '{}?{}'.format(reverse('checkout:index'), urlencode(url_query_parameters))

        return redirect(url)
