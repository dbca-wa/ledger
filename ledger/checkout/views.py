import logging
from django.utils import six
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext as _
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
#
from oscar.apps.payment import forms, models
from oscar.core.loading import get_class, get_model, get_classes
from oscar.apps.checkout import signals
from oscar.apps.shipping.methods import NoShippingRequired
#
from ledger.payments.models import Invoice
from ledger.accounts.models import EmailUser
from ledger.payments.facade import invoice_facade, bpoint_facade, bpay_facade

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

# Standard logger for checkout events
logger = logging.getLogger('oscar.checkout')

class IndexView(CoreIndexView):

    success_url = reverse_lazy('checkout:payment-details')
    class FallbackMissing(Exception):
        pass

    def validate_ledger(self,details):
        # validate there is a fallback url
        self.__validate_url(details.get('fallback_url'),'fallback')
        # validate card method to be used
        self.__validate_card_method(details.get('card_method'))
        # validate template if its present
        self.__validate_template(details.get('template'))
        # validate system id
        self.__validate_system(details.get('system_id'))
        # validate return url
        self.__validate_url(details.get('return_url'),'return')
        # validate bpay if present
        self.__validate_bpay(details.get('bpay_details'))
        # validate basket owner if present
        self.__validate_basket_owner(details.get('basket_owner'))
        # validate token details
        self.__validate_token_details(details.get('checkoutWithToken'))
        return True

    def __validate_token_details(self, details):
        ''' Check the token details to set the checkout session data
        '''
        # Check checkout with token parameter
        if not details:
            self.checkout_session.checkout_using_token(False)
        elif details == 'true' or details == 'True':
            self.checkout_session.checkout_using_token(True)

    def __validate_basket_owner(self,user_id):
        ''' Check if the user entered for basket and order swapping is valid
        '''
        user = None
        if user_id:
            try:
                user = EmailUser.objects.get(id=user_id)
            except EmailUser.DoesNotExist:
                raise
            if user:
                self.checkout_session.owned_by(user.id)

    def __validate_system(self, system):
        ''' Validate the system id
        '''
        valid_systems = [
            '0369'
        ]
        if not system:
            raise ValueError('System id required. eg ?system_id=<id>')
        elif not len(system) == 4:
            raise ValueError('The system id should be 4 characters long.')
        elif system not in valid_systems:
            raise ValueError('The System id is not valid.')
        self.checkout_session.use_system(system)

    def __validate_url(self, url, _type):
        if not url and _type == 'return':
            raise ValueError('Return url is required. eg ?return_url=')
        elif not url and _type == 'fallback':
            msg = 'A fallback url is required. eg ?fallback_url=<url>'
            messages.error(self.request,msg)
            raise self.FallbackMissing()

            #return HttpResponseRedirect(reverse('payments:payments-error'))
        self.checkout_session.return_to(url)

    def __validate_card_method(self, method):
        ''' Validate if the card method is payment or preauth
        '''
        if method in ['preauth','payment']:
            # 
            self.checkout_session.charge_by(method)

    def __validate_template(self, template_url):
        ''' Validate if the template exists
        '''
        if template_url:
            try:
                get_template(template_url)
                #
                self.checkout_session.use_template(template_url)
            except TemplateDoesNotExist:
                raise 
        return True

    def __validate_bpay(self,details):
        ''' Validate all the bpay data
        '''
        if details.get('bpay_format') == 'crn':
            self.checkout_session.bpay_using(details.get('bpay_format'))
            return True
        elif details.get('bpay_format') == 'icrn':
            if details.get('icrn_format') == 'ICRNAMT':
                self.checkout_session.bpay_using(details.get('bpay_format'))
                self.checkout_session.icrn_using(details.get('icrn_format'))
            elif details.get('icrn_format') in ['ICRNDATE','ICRAMTDATE'] and details.get('icrn_date'):
                self.checkout_session.bpay_using(details.get('bpay_format'))
                self.checkout_session.icrn_using(details.get('icrn_format'))
                self.checkout_session.bpay_by(details.get('icrn_date'))
            else:
                pass

    def get(self, request, *args, **kwargs):
        # We redirect immediately to shipping address stage if the user is
        # signed in.
        if request.user.is_authenticated():
            # We raise a signal to indicate that the user has entered the
            # checkout process so analytics tools can track this event.
            signals.start_checkout.send_robust(
                sender=self, request=request)
            # Set session variables that are required by ledger
            ledger_details = {
                'card_method': request.GET.get('card_method','payment'),
                'basket_owner': request.GET.get('basket_owner',None),
                'template': request.GET.get('template',None),
                'fallback_url': request.GET.get('fallback_url',None),
                'return_url': request.GET.get('return_url',None),
                'system_id': request.GET.get('system_id',None),
                'checkoutWithToken': request.GET.get('checkoutWithToken',False),
                'bpay_details': {
                    'bpay_format': request.GET.get('bpay_method','crn'),
                    'icrn_format': request.GET.get('icrn_format','ICRNAMT'),
                    'icrn_date': request.GET.get('icrn_date', None),
                }
            }
            # Check if all the required parameters are set
            # and redirect to appropriate page if not
            try:
                self.validate_ledger(ledger_details)
            except ValueError as e:
                messages.error(request,str(e))
                return HttpResponseRedirect(ledger_details.get('fallback_url'))
            except EmailUser.DoesNotExist as e:
                messages.error(request,str(e))
                return HttpResponseRedirect(ledger_details.get('fallback_url'))
            except self.FallbackMissing as e:
                return HttpResponseRedirect(reverse('payments:payments-error'))

            return self.get_success_response()
        return super(IndexView, self).get(request, *args, **kwargs)

class PaymentDetailsView(CorePaymentDetailsView):

    pre_conditions = [
        'check_basket_is_not_empty',
        'check_basket_is_valid',
        'check_user_email_is_captured',
        'check_shipping_data_is_captured'
    ]

    def get(self, request, *args, **kwargs):
        return super(PaymentDetailsView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Add data for Bpoint.
        """
        # Override method so the bankcard and billing address forms can be
        # added to the context.
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        method = self.checkout_session.payment_method()
        custom_template = self.checkout_session.custom_template()
        if not self.checkout_session.checkoutWithToken():
            ctx['store_card'] = True
        ctx['custom_template'] = custom_template
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
        else:
            # Get the payment method either card or other
            payment_method = request.POST.get('payment_method','')
            self.checkout_session.pay_by(payment_method)
            # Get if user wants to store the card
            store_card = request.POST.get('store_card',False)
            self.checkout_session.permit_store_card(bool(store_card))
        bankcard_form = forms.BankcardForm(request.POST)
        if payment_method == 'card':
            if not bankcard_form.is_valid():
                # Form validation failed, render page again with errors
                self.preview = False
                ctx = self.get_context_data(
                    bankcard_form=bankcard_form)
                return self.render_to_response(ctx)

        # Render preview with bankcard hidden
        if payment_method == 'card':
            return self.render_preview(request,bankcard_form=bankcard_form)
        else:
            return self.render_preview(request)

    def do_place_order(self, request):
        # Helper method to check that the hidden forms wasn't tinkered
        # with.
        bankcard_form = forms.BankcardForm(request.POST)
        if not bankcard_form.is_valid():
            messages.error(request, "Invalid submission")
            return HttpResponseRedirect(reverse('checkout:payment-details'))

        # Attempt to submit the order, passing the bankcard object so that it
        # gets passed back to the 'handle_payment' method below.
        submission = self.build_submission()
        submission['payment_kwargs']['bankcard'] = bankcard_form.bankcard
        return self.submit(**submission)

    def doInvoice(self,order_number,total,**kwargs):
        method = self.checkout_session.bpay_method()
        system = self.checkout_session.system()
        icrn_format = self.checkout_session.icrn_format()
        # Generate the string to be used to generate the icrn
        crn_string = '{0}{1}'.format(system,order_number)
        if method == 'crn':
            return invoice_facade.create_invoice_crn(
                order_number,
                total.incl_tax,
                crn_string) 
        elif method == 'icrn':
            return invoice_facade.create_invoice_icrn(
                order_number,
                total.incl_tax,
                crn_string,
                icrn_format)
        else:
            raise ValueError('{0} is not a supported BPAY method.'.format(method))

    def handle_payment(self, order_number, total, **kwargs):
        """
        Make submission
        """
        # Using preauth here (two-stage model). You could use payment to
        # perform the preauth and capture in one step.  
        method = self.checkout_session.payment_method()
        if method == 'card':
            try:
                #Generate Invoice
                invoice = self.doInvoice(order_number,total)
                # Swap user if in session
                if self.checkout_session.basket_owner():
                    user = EmailUser.objects.get(id=int(self.checkout_session.basket_owner()))
                else:
                    user = self.request.user
                # Check if the system only uses checkout with token for cards
                if self.checkout_session.checkoutWithToken():
                    resp = bpoint_facade.checkout_with_token(user,invoice.reference,kwargs['bankcard'])
                else:
                    # Store card if user wants to store card
                    if self.checkout_session.store_card():
                        bpoint_facade.checkout_with_token(user,invoice.reference,kwargs['bankcard'])
                    # Get the payment action for bpoint
                    card_method = self.checkout_session.card_method()
                    resp = bpoint_facade.post_transaction(card_method,'internet','single',order_number,invoice.reference, total.incl_tax,kwargs['bankcard'])
                    # Record payment source and event
                    source_type, is_created = models.SourceType.objects.get_or_create(
                        name='Bpoint')
                    # amount_allocated if action is preauth and amount_debited if action is payment
                    source = source_type.sources.model(
                        source_type=source_type,
                        amount_debited=total.incl_tax, currency=total.currency)
                    self.add_payment_source(source)
                    self.add_payment_event('Paid', total.incl_tax)
            except Exception as e:
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
                      "order - no payment has been taken.  Please "
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
            msg = six.text_type(e) + '. You can alternatively use the pay later option.'
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