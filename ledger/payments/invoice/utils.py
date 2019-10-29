from ledger.basket import models
from oscar.apps.order import utils
from django.conf import settings
from oscar.core.loading import get_class, get_model
from oscar.apps.order.utils import OrderCreator as CoreOrderCreator
from oscar.apps.order import exceptions
from oscar.apps.checkout.calculators import OrderTotalCalculator
from ledger.payments.invoice import facade as invoice_facade
from ledger.payments.utils import systemid_check, update_payments
from decimal import Decimal
import datetime

Order = get_model('order', 'Order')
Line = get_model('order', 'Line')
OrderDiscount = get_model('order', 'OrderDiscount')
order_placed = get_class('order.signals', 'order_placed')


class ShippingCharge():
    incl_tax = Decimal('0.00')
    excl_tax = Decimal('0.00')

    def is_tax_known(self):
        return False

class ShippingMethod():
    name = 'No shipping required'
    code = 'no-shipping-required'

class CreateInvoiceBasket(CoreOrderCreator):
    """
    This will create and invoice and order from a basket bypassing the session
    and payment bpoint code constraints.

    """

    def __init__(self, system=None, payment_method=None):
        self.system = system
        self.payment_method = payment_method

    def create_invoice_and_order(self,basket, total,
                    shipping_method, shipping_charge, user=None,
                    shipping_address=None, billing_address=None,
                    order_number=None, status=None, invoice_text='', **kwargs):

        """
        Creates and order from the basket and generates a new invoice.
        """

        basket = models.Basket.objects.get(id=basket.id)
        shipping_charge = ShippingCharge()
        shipping_method = ShippingMethod()
        total = self.get_order_totals(basket, shipping_charge, **kwargs)
        if basket.is_empty:
            raise ValueError(_("Empty baskets cannot be submitted"))
        if not order_number:
           generator = utils.OrderNumberGenerator()
           order_number = generator.order_number(basket)
        if not status and hasattr(settings, 'OSCAR_INITIAL_ORDER_STATUS'):
            status = getattr(settings, 'OSCAR_INITIAL_ORDER_STATUS')
        try:
            Order._default_manager.get(number=order_number)
        except Order.DoesNotExist:
            pass
        else:
            print ('ledger failed')
            print (order_number)
            raise ValueError(_("There is already an order with number %s")
                             % order_number)

        # Ok - everything seems to be in order, let's place the order
        order = self.create_order_model(
            user, basket, shipping_address, shipping_method, shipping_charge,
            billing_address, total, order_number, status, **kwargs)
        for line in basket.all_lines():
            if not basket.custom_ledger:
                self.create_line_models(order, line)
                self.update_stock_records(line)
            else:
                self.create_line_models(order,line,custom_ledger=True)

        # Record any discounts associated with this order
        for application in basket.offer_applications:
            # Trigger any deferred benefits from offers and capture the
            # resulting message
            application['message'] \
                = application['offer'].apply_deferred_benefit(basket, order,
                                                              application)
            # Record offer application results
            if application['result'].affects_shipping:
                # Skip zero shipping discounts
                shipping_discount = shipping_method.discount(basket)
                if shipping_discount <= D('0.00'):
                    continue
                # If a shipping offer, we need to grab the actual discount off
                # the shipping method instance, which should be wrapped in an
                # OfferDiscount instance.
                application['discount'] = shipping_discount
            self.create_discount_model(order, application)
            self.record_discount(application)

        for voucher in basket.vouchers.all():
            self.record_voucher_usage(order, voucher, user)

        # Send signal for analytics to pick up, but only if we aren't in a transaction block
        #if transaction.get_autocommit():
        #    order_placed.send(sender=self, order=order, user=user)
        invoice = self.create_invoice(order_number,total,invoice_text,**kwargs)
        basket.status = 'Submitted'
        basket.date_submitted = datetime.datetime.now()
        basket.save()

        return order

    def create_line_models(self, order, basket_line, extra_line_fields=None,custom_ledger=False):
        """
        Create the batch line model.
        You can set extra fields by passing a dictionary as the
        extra_line_fields value
        """
        product = basket_line.product
        stockrecord = basket_line.stockrecord
        if not stockrecord and not custom_ledger:
            raise exceptions.UnableToPlaceOrder(
                "Baket line #%d has no stockrecord" % basket_line.id)
        if not custom_ledger:
            partner = stockrecord.partner
        else:
            partner = None
        line_data = {
            'order': order,
            # Partner details
            'partner': partner if partner else None,
            'partner_name': partner.name if partner else None,
            'partner_sku': stockrecord.partner_sku  if partner else None,
            'stockrecord': stockrecord  if stockrecord else None,
            # Product details
            'product': product,
            'title': product.get_title() if not custom_ledger else basket_line.ledger_description,
            'upc': product.upc if product else None,
            'quantity': basket_line.quantity,
            'oracle_code': product.oracle_code if not custom_ledger else basket_line.oracle_code,
            # Price details
            'line_price_excl_tax':
            basket_line.line_price_excl_tax_incl_discounts,
            'line_price_incl_tax':
            basket_line.line_price_incl_tax_incl_discounts,
            'line_price_before_discounts_excl_tax':
            basket_line.line_price_excl_tax,
            'line_price_before_discounts_incl_tax':
            basket_line.line_price_incl_tax,
            # Reporting details
            'unit_cost_price': stockrecord.cost_price if stockrecord else basket_line.unit_price_incl_tax,
            'unit_price_incl_tax': basket_line.unit_price_incl_tax,
            'unit_price_excl_tax': basket_line.unit_price_excl_tax,
            'unit_retail_price': stockrecord.price_retail if stockrecord else basket_line.unit_price_incl_tax,
            # Shipping details
            'est_dispatch_date': basket_line.purchase_info.availability.dispatch_date if not custom_ledger else None,
            'line_status':  basket_line.line_status
        }

        extra_line_fields = extra_line_fields or {}
        if hasattr(settings, 'OSCAR_INITIAL_LINE_STATUS'):
            if not (extra_line_fields and 'status' in extra_line_fields):
                extra_line_fields['status'] = getattr(
                    settings, 'OSCAR_INITIAL_LINE_STATUS')
        if extra_line_fields:
            line_data.update(extra_line_fields)

        order_line = Line._default_manager.create(**line_data)
        self.create_line_price_models(order, order_line, basket_line)
        self.create_line_attributes(order, order_line, basket_line)
        self.create_additional_line_models(order, order_line, basket_line)
        return order_line

    def get_order_totals(self, basket, shipping_charge, **kwargs):
        """
        Returns the total for the order with and without tax
        """
        return OrderTotalCalculator(self).calculate(
            basket, shipping_charge, **kwargs)

    def create_invoice(self,order_number,total,invoice_text,**kwargs):
        """
        Create  and invoice for matching order.
        """
        method = 'crn'
        if self.system is None:
            self.system = settings.PS_PAYMENT_SYSTEM_ID

        # Generate the string to be used to generate the icrn
        crn_string = '{0}{1}'.format(systemid_check(self.system),order_number)
        return invoice_facade.create_invoice_crn(
             order_number,
             total.incl_tax,
             crn_string,
             self.system,
             invoice_text,
             self.payment_method,
        )

