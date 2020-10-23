from django.conf import settings
from django.contrib import messages
from django.core.signing import BadSignature, Signer
from django.utils.functional import SimpleLazyObject, empty
from django.utils.translation import ugettext_lazy as _

from oscar.core.compat import MiddlewareMixin, user_is_authenticated
from oscar.core.loading import get_class, get_model

Basket = get_model('basket', 'basket')
import hashlib

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
                #basket = Basket.objects.get(pk=basket_id, owner=None, status=Basket.OPEN)
                basket = Basket.objects.get(pk=basket_id)
                if basket.status != 'OPEN' or basket.status != 'SUBMITTED':
                      pass
                else:
                    basket = None
            except (BadSignature, Basket.DoesNotExist):
                request.cookies_to_delete.append(cookie_key)
        return basket

    def get_basket_hash(self, basket_id):
        return Signer(sep='|').sign(basket_id)

    def get_basket(self, request):
        """
        Return the open basket for this request
        """
        if request._basket_cache is not None:
            return request._basket_cache

        num_baskets_merged = 0
        manager = Basket.open
        cookie_key = self.get_cookie_key(request)
        cookie_basket = self.get_cookie_basket(cookie_key, request, manager)

        if cookie_basket:
            basket = cookie_basket
        else:

            if hasattr(request, 'user') and user_is_authenticated(request.user):
                # Signed-in user: if they have a cookie basket too, it means
                # that they have just signed in and we need to merge their cookie
                # basket into their user basket, then delete the cookie.
                try:
                    basket, __ = manager.get_or_create(owner=request.user)
                except Basket.MultipleObjectsReturned:
                    # Not sure quite how we end up here with multiple baskets.
                    # We merge them and create a fresh one
                    old_baskets = list(manager.filter(owner=request.user))
                    basket = old_baskets[0]
                    for other_basket in old_baskets[1:]:
                        self.merge_baskets(basket, other_basket)
                        num_baskets_merged += 1

                # Assign user onto basket to prevent further SQL queries when
                # basket.owner is accessed.
                basket.owner = request.user

                #if cookie_basket:
                #    self.merge_baskets(basket, cookie_basket)
                #    num_baskets_merged += 1
                #    request.cookies_to_delete.append(cookie_key)

            else:
                # Anonymous user with no basket - instantiate a new basket
                # instance.  No need to save yet.
                basket = Basket()

        # Cache basket instance for the during of this request
        request._basket_cache = basket

        if num_baskets_merged > 0:
            messages.add_message(request, messages.WARNING,
                                 _("We have merged a basket from a previous session. Its contents "
                                   "might have changed."))
        return basket

