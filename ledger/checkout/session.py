from oscar.apps.checkout.session import CheckoutSessionMixin as CoreCheckoutSessionMixin
from oscar.apps.checkout import exceptions
from django.core.urlresolvers import reverse
from django.contrib import messages

class CheckoutSessionMixin(CoreCheckoutSessionMixin):

    def skip_payment_if_proxy(self, request):
        if not self.preview and self.checkout_session.proxy():
            raise exceptions.PassedSkipCondition(
                url=reverse('checkout:preview')
            )

    def check_if_checkout_is_active(self, request):
        msg = 'There isn\'t an active checkout session available.'
        if not self.checkout_session.system():
            messages.error(self.request,msg)
            raise exceptions.FailedPreCondition(
                url=reverse('payments:payments-error')
            )