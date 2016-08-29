from oscar.apps.checkout.session import CheckoutSessionMixin as CoreCheckoutSessionMixin
from oscar.apps.checkout import exceptions
from django.core.urlresolvers import reverse

class CheckoutSessionMixin(CoreCheckoutSessionMixin):

    def skip_payment_if_proxy(self, request):
        if not self.preview and self.checkout_session.proxy():
            raise exceptions.PassedSkipCondition(
                url=reverse('checkout:preview')
            )