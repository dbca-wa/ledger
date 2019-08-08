from oscar.apps.checkout import exceptions
from django.core.urlresolvers import reverse
from django.contrib import messages
from oscar.core.loading import get_class
from decimal import Decimal as D


CoreCheckoutSessionMixin = get_class('checkout.session', 'CheckoutSessionMixin')

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

    def check_basket_is_valid(self, request):
        """
        Check that the basket is permitted to be submitted as an order. That
        is, all the basket lines are available to buy - nothing has gone out of
        stock since it was added to the basket.
        """
        messages = []
        strategy = request.strategy
        if not request.basket.custom_ledger:
            for line in request.basket.all_lines():
                result = strategy.fetch_for_line(line)
                is_permitted, reason = result.availability.is_purchase_permitted(
                    line.quantity)
                if not is_permitted:
                    # Create a more meaningful message to show on the basket page
                    msg = _(
                        "'%(title)s' is no longer available to buy (%(reason)s). "
                        "Please adjust your basket to continue"
                    ) % {
                        'title': line.product.get_title(),
                        'reason': reason}
                    messages.append(msg)
        if messages:
            raise exceptions.FailedPreCondition(
                url=reverse('basket:summary'),
                messages=messages
            )

    def skip_unless_basket_requires_shipping(self, request):
        # Check to see that a shipping address is actually required.  It may
        # not be if the basket is purely downloads
        if not request.basket.is_shipping_required():
            raise exceptions.PassedSkipCondition(
                url=reverse('checkout:shipping-method')
            )

    def check_shipping_data_is_captured(self, request):
        if not request.basket.is_shipping_required():
            # Even without shipping being required, we still need to check that
            # a shipping method code has been set.
            if not self.checkout_session.is_shipping_method_set(
                    self.request.basket):
                raise exceptions.FailedPreCondition(
                    url=reverse('checkout:shipping-method'),
                )
            return

        # Basket requires shipping: check address and method are captured and
        # valid.
        self.check_a_valid_shipping_address_is_captured()
        self.check_a_valid_shipping_method_is_captured()

    def check_a_valid_shipping_address_is_captured(self):
        # Check that shipping address has been completed
        if not self.checkout_session.is_shipping_address_set():
            raise exceptions.FailedPreCondition(
                url=reverse('checkout:shipping-address'),
                message=_("Please choose a shipping address")
            )

        # Check that the previously chosen shipping address is still valid
        shipping_address = self.get_shipping_address(
            basket=self.request.basket)
        if not shipping_address and not self.request.basket.custom_ledger:
            raise exceptions.FailedPreCondition(
                url=reverse('checkout:shipping-address'),
                message=_("Your previously chosen shipping address is "
                          "no longer valid.  Please choose another one")
            )

    def check_payment_data_is_captured(self, request):
        # this method only ever gets invoked when visiting checkout:preview

        # let POST requests through
        if request.method == 'POST':
            return

        # Check to see if payment is actually required for this order.
        shipping_address = self.get_shipping_address(request.basket)
        shipping_method = self.get_shipping_method(
            request.basket, shipping_address)
        if shipping_method:
            shipping_charge = shipping_method.calculate(request.basket)
        else:
            # It's unusual to get here as a shipping method should be set by
            # the time this skip-condition is called. In the absence of any
            # other evidence, we assume the shipping charge is zero.
            shipping_charge = prices.Price(
                currency=request.basket.currency, excl_tax=D('0.00'),
                tax=D('0.00')
            )
        total = self.get_order_totals(request.basket, shipping_charge)

        # bounce requests without a payment method set
        if not self.checkout_session.payment_method() and total.excl_tax != D('0.00'):
            raise exceptions.FailedPreCondition(
                url=reverse('checkout:payment-details'),
            )

        # bounce requests which specify a card,
        # as the CC info only exists on the page and not in the DB
        if self.checkout_session.payment_method() == 'card':
            raise exceptions.FailedPreCondition(
                url=reverse('checkout:payment-details'),
            )

    def build_submission(self, **kwargs):
        """
        Return a dict of data that contains everything required for an order
        submission.  This includes payment details (if any).
        This can be the right place to perform tax lookups and apply them to
        the basket.
        """
        basket = kwargs.get('basket', self.request.basket)
        shipping_address, billing_address, shipping_method, shipping_charge ,total = None, None, None, None, None
        shipping_address = self.get_shipping_address(basket)
        shipping_method = self.get_shipping_method(
            basket, shipping_address)
        billing_address = self.get_billing_address(shipping_address)
        if not shipping_method:
            total = shipping_charge = None
        else:
            shipping_charge = shipping_method.calculate(basket)
            total = self.get_order_totals(
                basket, shipping_charge=shipping_charge)
        submission = {
            'user': self.request.user,
            'basket': basket,
            'shipping_address': shipping_address,
            'shipping_method': shipping_method,
            'shipping_charge': shipping_charge,
            'billing_address': billing_address,
            'order_total': total,
            'order_kwargs': {},
            'payment_kwargs': {}}

        # If there is a billing address, add it to the payment kwargs as calls
        # to payment gateways generally require the billing address. Note, that
        # it normally makes sense to pass the form instance that captures the
        # billing address information. That way, if payment fails, you can
        # render bound forms in the template to make re-submission easier.
        if billing_address:
            submission['payment_kwargs']['billing_address'] = billing_address

        # Allow overrides to be passed in
        submission.update(kwargs)

        # Set guest email after overrides as we need to update the order_kwargs
        # entry.
        if (not submission['user'].is_authenticated() and
                'guest_email' not in submission['order_kwargs']):
            email = self.checkout_session.get_guest_email()
            submission['order_kwargs']['guest_email'] = email
        return submission
