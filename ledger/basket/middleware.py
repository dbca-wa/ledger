from oscar.core.loading import get_class, get_model
from django.core.signing import BadSignature, Signer


Basket = get_model('basket', 'basket')

# stupid shim to work around Python 2's broken handling of cookies with : in them
# http://bugs.python.org/issue2193
# (we replace them with a |)
# can be safely ditched when we move to Python 3

from oscar.apps.basket.middleware import BasketMiddleware as CoreBasketMiddleware

class BasketMiddleware(CoreBasketMiddleware):

    # required for python 3
    def __init__(self):
        #response = self.get_response(request)
        return None

    def get_cookie_basket(self, cookie_key, request, manager):
        """
        Looks for a basket which is referenced by a cookie.

        If a cookie key is found with no matching basket, then we add
        it to the list to be deleted.
        """
        basket = None
        if cookie_key in request.COOKIES:
            basket_hash = request.COOKIES[cookie_key]
            try:
                basket_id = Signer(sep='|').unsign(basket_hash)
                basket = Basket.objects.get(pk=basket_id, owner=None,
                                            status=Basket.OPEN)
            except (BadSignature, Basket.DoesNotExist):
                request.cookies_to_delete.append(cookie_key)
        return basket

    def get_basket_hash(self, basket_id):
        return Signer(sep='|').sign(basket_id)
