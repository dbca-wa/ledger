import logging
import requests
import json
from requests.exceptions import HTTPError, ConnectionError
import traceback
from decimal import Decimal as D
from django.db import transaction
from django.conf import settings
from django.core.validators import URLValidator
from django.utils import six
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.template.loader import get_template
#
from ledger.payment import forms, models
from ledger.payments.helpers import is_payment_admin
from oscar.core.loading import get_class, get_model, get_classes
from oscar.apps.checkout import signals
from oscar.apps.shipping.methods import NoShippingRequired
#
from ledger.payments.models import Invoice, BpointToken
from ledger.accounts.models import EmailUser
from ledger.payments.facade import invoice_facade, bpoint_facade, bpay_facade
from ledger.payments.utils import isLedgerURL, systemid_check

Order = get_model('order', 'Order')
CorePaymentDetailsView = get_class('checkout.views','PaymentDetailsView')
CoreIndexView = get_class('checkout.views','IndexView')
CoreThankYouView = get_class('checkout.views','ThankYouView')
UserAddress = get_model('address','UserAddress')
RedirectRequired, UnableToTakePayment, PaymentError \
    = get_classes('payment.exceptions', ['RedirectRequired',
                                         'UnableToTakePayment',
                                         'PaymentError'])
UnableToPlaceOrder = get_class('order.exceptions', 'UnableToPlaceOrder')
CheckoutSessionData = get_class(
    'checkout.utils', 'CheckoutSessionData')

# Standard logger for checkout events
logger = logging.getLogger('oscar.checkout')

class IndexView(CoreIndexView):

    success_url = reverse_lazy('checkout:payment-details')
    class FallbackMissing(Exception):
        pass

    def proper_errorpage(self,url,r,e):
        messages.error(r,str(e))
        if isLedgerURL(url):
            return HttpResponseRedirect(url)
        else:
            return HttpResponseRedirect(reverse('payments:payments-error'))

    def get(self, request, *args, **kwargs):
        # We redirect immediately to shipping address stage if the user is
        # signed in.
        if True:
            # We raise a signal to indicate that the user has entered the
            # checkout process so analytics tools can track this event.
            signals.start_checkout.send_robust(
                sender=self, request=request)

            return self.get_success_response()
        return super(IndexView, self).get(request, *args, **kwargs)

class PaymentDetailsView(CorePaymentDetailsView):

    pre_conditions = [
        'check_if_checkout_is_active',
        'check_basket_is_not_empty',
        'check_basket_is_valid',
        'check_user_email_is_captured',
        'check_shipping_data_is_captured'
    ]

    def get_skip_conditions(self, request):
        if not self.preview:
            # Payment details should only be collected if necessary
            return ['skip_unless_payment_is_required','skip_payment_if_proxy']
        return super(PaymentDetailsView, self).get_skip_conditions(request)

    def get(self, request, *args, **kwargs):
        if self.skip_preview_if_free(request) or self.skip_if_proxy():
             return self.handle_place_order_submission(request)
        if self.checkout_session.proxy() and not self.preview:
            self.checkout_session.pay_by('other')
        return super(PaymentDetailsView, self).get(request, *args, **kwargs)

    def skip_if_proxy(self):
        if self.preview and self.checkout_session.proxy():
            return True
        return False

    def skip_preview_if_free(self, request):
        if self.preview:
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
            if total.excl_tax == D('0.00'):
                self.checkout_session.is_free_basket(True)
                return True
        return False

    def get_context_data(self, **kwargs):
        """
        Add data for Bpoint.
        """
        # Override method so the bankcard and billing address forms can be
        # added to the context.
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        method = self.checkout_session.payment_method()
        custom_template = self.checkout_session.custom_template()

        ctx['store_card'] = True
        user = None
        # only load stored cards if the user is an admin or has legitimately logged in
        if self.checkout_session.basket_owner() and is_payment_admin(self.request.user):
            user = EmailUser.objects.get(id=int(self.checkout_session.basket_owner()))
        elif self.request.user.is_authenticated():
            user = self.request.user

        if user:
            cards = user.stored_cards.all()
            if cards:
                ctx['cards'] = cards

        ctx['custom_template'] = custom_template
        ctx['bpay_allowed'] = settings.BPAY_ALLOWED
        ctx['payment_method'] = method
        ctx['bankcard_form'] = kwargs.get(
            'bankcard_form', forms.BankcardForm())
        ctx['billing_address_form'] = kwargs.get(
            'billing_address_form', forms.BillingAddressForm())
        return ctx

    def post(self, request, *args, **kwargs):
        # Override so we can validate the bankcard/billingaddress submission.
        # If it is valid, we render the preview screen with the forms hidden
        # within it.  When the preview is submitted, we pick up the 'action'
        # parameters and actually place the order.
        if request.POST.get('action', '') == 'place_order':
            if self.checkout_session.payment_method() == 'card':
                return self.do_place_order(request)
            else:
                return self.handle_place_order_submission(request)
        # Validate the payment method
        payment_method = request.POST.get('payment_method', '')
        if payment_method == 'bpay' and settings.BPAY_ALLOWED:
            self.checkout_session.pay_by('bpay')
        elif payment_method == 'card':
            self.checkout_session.pay_by('card')
        elif payment_method: # someone's trying to pull a fast one, refresh the page
            self.preview = False
            return self.render_to_response(self.get_context_data())

        # Get if user wants to store the card
        store_card = request.POST.get('store_card',False)
        self.checkout_session.permit_store_card(bool(store_card))
        # Get if user wants to checkout using a stored card
        checkout_token = request.POST.get('checkout_token',False)
        if checkout_token:
            self.checkout_session.checkout_using_token(request.POST.get('card',''))

        if self.checkout_session.payment_method() == 'card' and not checkout_token:
            bankcard_form = forms.BankcardForm(request.POST)
            if not bankcard_form.is_valid():
                # Form validation failed, render page again with errors
                self.preview = False
                ctx = self.get_context_data(
                    bankcard_form=bankcard_form)
                return self.render_to_response(ctx)

        # Render preview with bankcard hidden
        if self.checkout_session.payment_method() == 'card' and not checkout_token:
            return self.render_preview(request,bankcard_form=bankcard_form)
        else:
            return self.render_preview(request)

    def do_place_order(self, request):
        # Helper method to check that the hidden forms wasn't tinkered
        # with.
        if not self.checkout_session.checkout_token():
            bankcard_form = forms.BankcardForm(request.POST)
            if not bankcard_form.is_valid():
                messages.error(request, "Invalid submission")
                return HttpResponseRedirect(reverse('checkout:payment-details'))

        # Attempt to submit the order, passing the bankcard object so that it
        # gets passed back to the 'handle_payment' method below.
        submission = self.build_submission()
        if not self.checkout_session.checkout_token():
            submission['payment_kwargs']['bankcard'] = bankcard_form.bankcard
        return self.submit(**submission)

    def doInvoice(self,order_number,total,**kwargs):
        method = self.checkout_session.bpay_method()
        system = self.checkout_session.system()
        icrn_format = self.checkout_session.icrn_format()
        # Generate the string to be used to generate the icrn
        crn_string = '{0}{1}'.format(systemid_check(system),order_number)
        if method == 'crn':
            return invoice_facade.create_invoice_crn(
                order_number,
                total.incl_tax,
                crn_string,
                system,
                self.checkout_session.get_invoice_text() if self.checkout_session.get_invoice_text() else '',
                self.checkout_session.payment_method() if self.checkout_session.payment_method() else None
            )
        elif method == 'icrn':
            return invoice_facade.create_invoice_icrn(
                order_number,
                total.incl_tax,
                crn_string,
                icrn_format,
                system,
                self.checkout_session.get_invoice_text() if self.checkout_session.get_invoice_text() else '',
                self.checkout_session.payment_method() if self.checkout_session.payment_method() else None
            )

        else:
            raise ValueError('{0} is not a supported BPAY method.'.format(method))

    def handle_last_check(self,url):
        try:
            res = requests.get(url,cookies=self.request.COOKIES, verify=False)
            res.raise_for_status()
            response = json.loads(res.content.decode('utf-8')).get('status')
            if response != 'approved':
                error = json.loads(res.content.decode('utf-8')).get('error',None)
                if error:
                    raise ValueError('Payment could not be completed at this moment due to the following error \n {}'.format(error))
                else:
                    raise ValueError('Payment could not be completed at this moment.')
        except requests.exceptions.HTTPError as e:
            if 400 <= e.response.status_code < 500:
                http_error_msg = '{} Client Error: {} for url: {} > {}'.format(e.response.status_code, e.response.reason, e.response.url,e.response._content)

            elif 500 <= e.response.status_code < 600:
                http_error_msg = '{} Server Error: {} for url: {}'.format(e.response.status_code, e.response.reason, e.response.url)
            e.message = http_error_msg

            e.args = (http_error_msg,)
            raise PaymentError(e)

    def handle_payment(self, order_number, total, **kwargs):
        """
        Make submission
        """
        logger.info('Order #%s: handling payment', order_number)
        # Using preauth here (two-stage model). You could use payment to
        # perform the preauth and capture in one step.
        with transaction.atomic():
            method = self.checkout_session.payment_method()
            # Last point to use the check url to see if the payment should be permitted
            if self.checkout_session.get_last_check():
                self.handle_last_check(self.checkout_session.get_last_check())
            if self.checkout_session.free_basket():
                self.doInvoice(order_number,total)
            else:
                if method == 'card':
                    try:
                        #Generate Invoice
                        invoice = self.doInvoice(order_number,total)
                        # Swap user if in session
                        if self.checkout_session.basket_owner():
                            user = EmailUser.objects.get(id=int(self.checkout_session.basket_owner()))
                        else:
                            user = self.request.user
                        # Get the payment action for bpoint
                        card_method = self.checkout_session.card_method()
                        # Check if the user is paying using a stored card
                        if self.checkout_session.checkout_token():
                            try:
                                token = BpointToken.objects.get(id=self.checkout_session.checkout_token())
                            except BpointToken.DoesNotExist:
                                raise ValueError('This stored card does not exist.')
                            if self.checkout_session.invoice_association():
                                invoice.token = '{}|{}|{}'.format(token.DVToken,token.expiry_date.strftime("%m%y"),token.last_digits)
                                invoice.save()
                            else:
                                bpoint_facade.pay_with_storedtoken(card_method,'internet','single',token.id,order_number,invoice.reference, total.incl_tax)
                        else:
                            # Store card if user wants to store card
                            if self.checkout_session.store_card():
                                resp = bpoint_facade.create_token(user,invoice.reference,kwargs['bankcard'],True)
                                if self.checkout_session.invoice_association():
                                    invoice.token = resp
                                    invoice.save()
                                else:
                                    bankcard = kwargs['bankcard']
                                    bankcard.last_digits = bankcard.number[-4:]
                                    resp = bpoint_facade.post_transaction(card_method,'internet','single',order_number,invoice.reference, total.incl_tax,bankcard)
                            else:
                                if self.checkout_session.invoice_association():
                                    resp = bpoint_facade.create_token(user,invoice.reference,kwargs['bankcard'])
                                    invoice.token = resp
                                    invoice.save()
                                else:
                                    bankcard = kwargs['bankcard']
                                    bankcard.last_digits = bankcard.number[-4:]
                                    resp = bpoint_facade.post_transaction(card_method,'internet','single',order_number,invoice.reference, total.incl_tax,bankcard)
                        if not self.checkout_session.invoice_association():
                            # Record payment source and event
                            source_type, is_created = models.SourceType.objects.get_or_create(
                                name='Bpoint')
                            # amount_allocated if action is preauth and amount_debited if action is payment
                            if card_method == 'payment':
                                source = source_type.sources.model(
                                    source_type=source_type,
                                    amount_debited=total.incl_tax, currency=total.currency)
                            elif card_method == 'preauth':
                                source = source_type.sources.model(
                                    source_type=source_type,
                                    amount_allocated=total.incl_tax, currency=total.currency)
                            self.add_payment_source(source)
                            self.add_payment_event('Paid', total.incl_tax)
                    except Exception as e:
                        traceback.print_exc()
                        raise
                else:
                    #Generate Invoice
                    self.doInvoice(order_number,total)

    def submit(self, user, basket, shipping_address, shipping_method,  # noqa (too complex (10))
               shipping_charge, billing_address, order_total,
               payment_kwargs=None, order_kwargs=None):
        """
        Submit a basket for order placement.
        The process runs as follows:
         * Generate an order number
         * Freeze the basket so it cannot be modified any more (important when
           redirecting the user to another site for payment as it prevents the
           basket being manipulated during the payment process).
         * Attempt to take payment for the order
           - If payment is successful, place the order
           - If a redirect is required (eg PayPal, 3DSecure), redirect
           - If payment is unsuccessful, show an appropriate error message
        :basket: The basket to submit.
        :payment_kwargs: Additional kwargs to pass to the handle_payment
                         method. It normally makes sense to pass form
                         instances (rather than model instances) so that the
                         forms can be re-rendered correctly if payment fails.
        :order_kwargs: Additional kwargs to pass to the place_order method
        """
        if payment_kwargs is None:
            payment_kwargs = {}
        if order_kwargs is None:
            order_kwargs = {}

        # Taxes must be known at this point
        assert basket.is_tax_known, (
            "Basket tax must be set before a user can place an order")
        assert shipping_charge.is_tax_known, (
            "Shipping charge tax must be set before a user can place an order")

        # We generate the order number first as this will be used
        # in payment requests (ie before the order model has been
        # created).  We also save it in the session for multi-stage
        # checkouts (eg where we redirect to a 3rd party site and place
        # the order on a different request).
        order_number = self.generate_order_number(basket)
        self.checkout_session.set_order_number(order_number)
        logger.info("Order #%s: beginning submission process for basket #%d",
                    order_number, basket.id)

        # Freeze the basket so it cannot be manipulated while the customer is
        # completing payment on a 3rd party site.  Also, store a reference to
        # the basket in the session so that we know which basket to thaw if we
        # get an unsuccessful payment response when redirecting to a 3rd party
        # site.
        self.freeze_basket(basket)
        self.checkout_session.set_submitted_basket(basket)

        # We define a general error message for when an unanticipated payment
        # error occurs.
        error_msg = _("A problem occurred while processing payment for this "
                      "order - no payment has been taken.")
        if settings.BPAY_ALLOWED:
            error_msg += _("  Please "
                      "use the pay later option if this problem persists")

        signals.pre_payment.send_robust(sender=self, view=self)

        try:
            self.handle_payment(order_number, order_total, **payment_kwargs)
        except RedirectRequired as e:
            # Redirect required (eg PayPal, 3DS)
            logger.info("Order #%s: redirecting to %s", order_number, e.url)
            return http.HttpResponseRedirect(e.url)
        except UnableToTakePayment as e:
            # Something went wrong with payment but in an anticipated way.  Eg
            # their bankcard has expired, wrong card number - that kind of
            # thing. This type of exception is supposed to set a friendly error
            # message that makes sense to the customer.
            msg = six.text_type(e) + '.'
            if settings.BPAY_ALLOWED:
                msg += ' You can alternatively use the pay later option.'
            logger.warning(
                "Order #%s: unable to take payment (%s) - restoring basket",
                order_number, msg)
            self.restore_frozen_basket()

            # We assume that the details submitted on the payment details view
            # were invalid (eg expired bankcard).
            return self.render_payment_details(
                self.request, error=msg, **payment_kwargs)
        except PaymentError as e:
            # A general payment error - Something went wrong which wasn't
            # anticipated.  Eg, the payment gateway is down (it happens), your
            # credentials are wrong - that king of thing.
            # It makes sense to configure the checkout logger to
            # mail admins on an error as this issue warrants some further
            # investigation.
            msg = six.text_type(e)
            logger.error("Order #%s: payment error (%s)", order_number, msg,
                         exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs)
        except Exception as e:
            # Unhandled exception - hopefully, you will only ever see this in
            # development...
            traceback.print_exc()
            logger.error(
                "Order #%s: unhandled exception while taking payment (%s)",
                order_number, e, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=error_msg, **payment_kwargs)

        signals.post_payment.send_robust(sender=self, view=self)

        # If all is ok with payment, try and place order
        logger.info("Order #%s: payment successful, placing order",
                    order_number)
        try:
            return self.handle_order_placement(
                order_number, user, basket, shipping_address, shipping_method,
                shipping_charge, billing_address, order_total, **order_kwargs)
        except UnableToPlaceOrder as e:
            # It's possible that something will go wrong while trying to
            # actually place an order.  Not a good situation to be in as a
            # payment transaction may already have taken place, but needs
            # to be handled gracefully.
            msg = six.text_type(e)
            logger.error("Order #%s: unable to place order - %s",
                         order_number, msg, exc_info=True)
            self.restore_frozen_basket()
            return self.render_preview(
                self.request, error=msg, **payment_kwargs)


# =========
# Thank you
# =========

class ThankYouView(CoreThankYouView):
    """
    Displays the 'thank you' page which summarises the order just submitted.
    """
    template_name = 'checkout/thank_you.html'
    context_object_name = 'order'
    order_id = None
    return_url = None

    def get_context_data(self, **kwargs):
        # Override method so the return_url and order and invoice_id can be
        # added to the context.
        ctx = super(ThankYouView, self).get_context_data(**kwargs)
        order = ctx['order']
        invoice_ref = Invoice.objects.get(order_number=order.number).reference
        ctx['invoice_ref'] = invoice_ref
        ctx['return_url'] = '{}?order_id={}&invoice_ref={}'.format(self.return_url,order.id,invoice_ref)
        return ctx

    def get_object(self):
        # We allow superusers to force an order thank-you page for testing
        order = None
        if self.request.user.is_superuser:
            if 'order_number' in self.request.GET:
                order = Order._default_manager.get(
                    number=self.request.GET['order_number'])
            elif 'order_id' in self.request.GET:
                order = Order._default_manager.get(
                    id=self.request.GET['order_id'])

        if not order:
            if 'checkout_order_id' in self.request.session:
                order = Order._default_manager.get(
                    pk=self.request.session['checkout_order_id'])

                self.order_id = self.request.session['checkout_order_id']
            else:
                raise http.Http404(_("No order found"))

            if'checkout_return_url' in self.request.session:
                self.return_url = self.request.session['checkout_return_url']
                #del self.request.session['checkout_return_url']

        return order
