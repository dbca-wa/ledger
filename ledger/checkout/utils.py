from decimal import Decimal as D, getcontext

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from oscar.apps.checkout.utils import CheckoutSessionData as CoreCheckoutSessionData
from oscar.apps.voucher.models import Voucher
from oscar.core.loading import get_class
from ledger.accounts.models import EmailUser, Organisation
from ledger.checkout import serializers
from ledger.catalogue.models import Product
from ledger.basket.models import Basket
from ledger.basket.middleware import BasketMiddleware
from ledger.payments.models import Invoice
#from oscar.apps.order.models import Order
from ledger.order.models import Order
from django.core.signing import BadSignature, Signer
from django.core.exceptions import ValidationError
from confy import env
import os

Selector = get_class('partner.strategy', 'Selector')
selector = Selector()


def create_basket_session_v2(emailuser_id, parameters):
    ledger_product_custom_fields = ('ledger_description','quantity','price_incl_tax','oracle_code')

    print ("create_basket_session params v2")
    if emailuser_id:
        pass
    else:
        print ("USER IS NOT LOGGED IN")

    if 'tax_override' in parameters:
        if parameters['tax_override'] is True:
            ledger_product_custom_fields = ('ledger_description','quantity','price_incl_tax','price_excl_tax','oracle_code')
        if 'line_status' in parameters:
            if parameters['line_status'] is True:
                ledger_product_custom_fields = ('ledger_description','quantity','price_incl_tax','price_excl_tax','oracle_code', 'line_status')

    user_obj = EmailUser.objects.get(id=int(emailuser_id))
    serializer = serializers.BasketSerializer(data=parameters)
    serializer.is_valid(raise_exception=True)
    custom = serializer.validated_data.get('custom_basket')
    booking_reference = None
    booking_reference_link = None
    organisation_id=None

    if 'booking_reference' in parameters:
        booking_reference = serializer.validated_data['booking_reference']

    if 'booking_reference_link' in parameters:
        booking_reference_link = serializer.validated_data['booking_reference_link']

    if 'organisation' in parameters:
        organisation_id = serializer.validated_data['organisation']

    # validate product list
    if custom:
        product_serializer = serializers.CheckoutCustomProductSerializer(data=serializer.initial_data.get('products'), many=True)
    else:
        product_serializer = serializers.CheckoutProductSerializer(data=serializer.initial_data.get('products'), many=True)

    product_serializer.is_valid(raise_exception=True)
    # Cleaning up stale Baskets
    #if request.user:
    #   if request.user.__class__.__name__ == 'EmailUser':
    if user_obj:
          ba = Basket.objects.filter(owner=user_obj).exclude(status='Submitted').exclude(status='Saved')
          for b in ba:
              b.status='Frozen'
              b.save()

    # validate basket
    if serializer.validated_data.get('vouchers'):
        if custom:
            basket = createCustomBasketv2(serializer.validated_data['products'],
                                        user_obj, serializer.validated_data['system'],
                                        serializer.validated_data['vouchers'],True,booking_reference, booking_reference_link, organisation_id, ledger_product_custom_fields)
        else:
            basket = createBasket(serializer.validated_data['products'], user_obj,
                                    serializer.validated_data['system'],
                                    serializer.validated_data['vouchers'],True,booking_reference, booking_reference_link, organisation_id)
    else:
        if custom:
            basket = createCustomBasketv2(serializer.validated_data['products'],
                                        user_obj, serializer.validated_data['system'],None,True,booking_reference, booking_reference_link, organisation_id, ledger_product_custom_fields)
        else:
            basket = createBasket(serializer.validated_data['products'],
                                    user_obj, serializer.validated_data['system'],None,True,booking_reference, booking_reference_link, organisation_id)

    return basket, BasketMiddleware().get_basket_hash(basket.id)


# create a basket in Oscar.
# a basket contains the system ID, list of product line items, vouchers, and not much else.
def create_basket_session(request, parameters):
    print ("create_basket_session params")
    serializer = serializers.BasketSerializer(data=parameters)
    serializer.is_valid(raise_exception=True)
    custom = serializer.validated_data.get('custom_basket')
    booking_reference = None
    booking_reference_link = None
    if 'booking_reference' in parameters:
        booking_reference = serializer.validated_data['booking_reference']

    if 'booking_reference_link' in parameters:
        booking_reference_link = serializer.validated_data['booking_reference_link']

    # validate product list
    if custom:
        product_serializer = serializers.CheckoutCustomProductSerializer(data=serializer.initial_data.get('products'), many=True)
    else:
        product_serializer = serializers.CheckoutProductSerializer(data=serializer.initial_data.get('products'), many=True)

    product_serializer.is_valid(raise_exception=True)
    # Cleaning up stale Baskets
    if request.user:
       if request.user.__class__.__name__ == 'EmailUser':
          ba = Basket.objects.filter(owner=request.user).exclude(status='Submitted').exclude(status='Saved')
          for b in ba:
              b.status='Frozen'
              b.save()
    # validate basket
    if serializer.validated_data.get('vouchers'):
        if custom:
            basket = createCustomBasket(serializer.validated_data['products'],
                                        request.user, serializer.validated_data['system'],
                                        serializer.validated_data['vouchers'],True,booking_reference, booking_reference_link)
        else:
            basket = createBasket(serializer.validated_data['products'], request.user,
                                    serializer.validated_data['system'],
                                    serializer.validated_data['vouchers'],True,booking_reference, booking_reference_link)
    else:
        if custom:
            basket = createCustomBasket(serializer.validated_data['products'],
                                        request.user, serializer.validated_data['system'],None,True,booking_reference,booking_reference_link)
        else:
            basket = createBasket(serializer.validated_data['products'],
                                    request.user, serializer.validated_data['system'],None,True,booking_reference,booking_reference_link)

    return basket, BasketMiddleware().get_basket_hash(basket.id)


def use_existing_basket(basket):

    return basket, BasketMiddleware().get_basket_hash(basket.id)

def use_existing_basket_from_invoice(invoice): 
    
    inv = Invoice.objects.get(reference=invoice)
    order =  Order.objects.get(number=inv.order_number)
    basket = order.basket
    return basket, BasketMiddleware().get_basket_hash(order.basket.id)


def get_cookie_basket(cookie_key,request):
    basket = None
    if cookie_key in request.COOKIES:
       basket_hash = request.COOKIES[cookie_key]
       try:
           basket_id = Signer(sep='|').unsign(basket_hash)
           basket = Basket.objects.get(pk=basket_id,
                                      status=Basket.OPEN)
       except (BadSignature, Basket.DoesNotExist):
           request.cookies_to_delete.append(cookie_key)
       return basket
    return None


# create a checkout session in Oscar.
# the checkout session contains all of the attributes about a purchase session (e.g. payment method,
# shipping method, ID of the person performing the checkout)
def create_checkout_session(request, parameters):
    #print (parameters['user_logged_in'])
    serializer = serializers.CheckoutSerializer(data=parameters)
    try:
        serializer.is_valid(raise_exception=True)
    except Exception as e:
        raise ValidationError(str(e))
    try:
        session_data = CheckoutSessionData(request)
    except Exception as e:
        raise ValidationError(str(e))
    # reset method of payment when creating a new session
    session_data.pay_by(None)
    session_data.use_system(serializer.validated_data['system'])
    session_data.charge_by(serializer.validated_data['card_method'])
    session_data.use_shipping_method(serializer.validated_data['shipping_method'])
    session_data.owned_by(serializer.validated_data['basket_owner'])
    # FIXME: replace internal user ID with email address once lookup/alias issues sorted
    email = None
    if serializer.validated_data['basket_owner'] and request.user.is_anonymous():
        email = EmailUser.objects.get(id=serializer.validated_data['basket_owner']).email
    if email is None: 
        if 'session_type' in parameters:
             if parameters['session_type'] == 'ledger_api':
                  if parameters['user_logged_in']:
                      email = EmailUser.objects.get(id=serializer.validated_data['user_logged_in']).email
    session_data.set_guest_email(email)
    if 'user_logged_in' in parameters:
        if parameters['user_logged_in'] is not None:
            session_data.set_user_logged_in(parameters['user_logged_in'])
        else:
            session_data.set_user_logged_in(None)
    else:
        session_data.set_user_logged_in(None)
    session_data.use_template(serializer.validated_data['template'])
    # fallback url?
    session_data.return_to(serializer.validated_data['return_url'])
    session_data.return_preload_to(serializer.validated_data['return_preload_url'])
    session_data.associate_invoice(serializer.validated_data['associate_invoice_with_token'])
    session_data.redirect_forcefully(serializer.validated_data['force_redirect'])
    session_data.return_email(serializer.validated_data['send_email'])
    session_data.is_proxy(serializer.validated_data['proxy'])
    session_data.checkout_using_token(serializer.validated_data['checkout_token'])
    session_data.bpay_using(serializer.validated_data['bpay_format'])
    session_data.icrn_using(serializer.validated_data['icrn_format'])
    session_data.bpay_by(serializer.validated_data['icrn_date'])
    session_data.set_invoice_text(serializer.validated_data['invoice_text'])
    session_data.set_invoice_name(serializer.validated_data['invoice_name'])

    session_data.set_last_check(serializer.validated_data['check_url'])
    session_data.set_amount_override(serializer.validated_data['amount_override']) 
    if serializer.validated_data['session_type'] == 'ledger_api':
        session_data.set_session_type(serializer.validated_data['session_type'])
    else:
        session_data.set_session_type('standard')
    if 'response_type' in parameters:
        session_data.set_response_type(serializer.validated_data['response_type'])
    

# shortcut for finalizing a checkout session and creating an invoice.
# equivalent to checking out with a deferred payment method (e.g. BPAY).
# useful for internal booking methods being invoked from server-side.
def place_order_submission(request):
    from ledger.checkout.views import PaymentDetailsView
    cs = CheckoutSessionData(request)
    pdv = PaymentDetailsView(request=request, checkout_session=cs)
    pdv.get(request)
    result = pdv.handle_place_order_submission(request)
    return result


class CheckoutSessionData(CoreCheckoutSessionData):
    # Custom Ledger methods

    # Card Methods
    # ===========================
    def charge_by(self, method):
        self._set('ledger','card',method)

    def card_method(self):
        return self._get('ledger','card')

    # Return URL Methods
    # ===========================
    def return_to(self, url):
        self._set('ledger','return_url',url)

    def return_url(self):
        return self._get('ledger','return_url')

    def return_preload_to(self, url):
        self._set('ledger', 'return_preload_url', url)

    def return_preload_url(self):
        return self._get('ledger', 'return_preload_url')

    # Template Methods
    # ===========================
    def use_template(self, url):
        self._set('ledger','custom_template_url',url)

    def custom_template(self):
        return self._get('ledger','custom_template_url')

    # System Methods
    # ===========================
    def use_system(self, system_id):
        self._set('ledger','system_id',system_id)
        
    def system(self):
        return self._get('ledger','system_id')
    
    # BPAY Methods
    # ===========================
    def bpay_using(self, method):
        self._set('ledger','bpay_method',method)
 
    def bpay_method(self):
        return self._get('ledger','bpay_method')

    # BPAY ICRN Format
    # ===========================
    def icrn_using(self, _format):
        self._set('ledger', 'icrn_format',_format)

    def icrn_format(self):
        return self._get('ledger','icrn_format')

    # Basket owner
    # ===========================
    def owned_by(self, user_id):
        self._set('ledger','basket_owner',user_id)

    def basket_owner(self):
        return self._get('ledger','basket_owner')

    # BPAY due date
    # ===========================
    def bpay_by(self, due_date):
        self._set('ledger','due_date',due_date)

    def bpay_due(self):
        return self._get('ledger','due_date')

    # Checkout using Token
    # ===========================
    def checkout_using_token(self, token):
        self._set('ledger','checkout_token',token)

    def checkout_token(self):
        return self._get('ledger','checkout_token')

    # Associate token to invoice
    # ===========================
    def associate_invoice(self, status):
        self._set('ledger','associate_invoice',status)

    def invoice_association(self):
        return self._get('ledger','associate_invoice')

    # Store Card
    # ===========================
    def permit_store_card(self, status):
        self._set('ledger','store_card',status)

    def store_card(self):
        return self._get('ledger','store_card')

    # Redirection
    # ===========================
    def redirect_forcefully(self, status):
        self._set('ledger','force_redirect',status)

    def force_redirect(self):
        return self._get('ledger','force_redirect')

    # Basket Free
    # ===========================
    def is_free_basket(self, status):
        self._set('ledger','free_basket',status)

    def free_basket(self):
        return self._get('ledger','free_basket')

    # Proxy Payment
    # ===========================
    def is_proxy(self, status):
        self._set('ledger','proxy',status)

    def proxy(self):
        return self._get('ledger','proxy')

    # Email
    # ===========================
    def return_email(self, status):
        self._set('ledger','send_email',status)

    def send_email(self):
        return self._get('ledger','send_email')

    # Invoice Optional text
    # ==========================
    def set_invoice_text(self,text):
        self._set('ledger','invoice_text',text)

    def get_invoice_text(self):
        return self._get('ledger','invoice_text')


    # Invoice Name Override Account Name
    # ==========================
    def set_invoice_name(self,text):
        self._set('ledger','invoice_name',text)

    def get_invoice_name(self):
        return self._get('ledger','invoice_name')

    # Last check url per system 
    # ==========================
    def set_last_check(self,text):
        self._set('ledger','last_check',text)

    def get_last_check(self):
        return self._get('ledger','last_check')

    def set_amount_override(self,text):
        self._set('ledger','amount_override',text)

    def get_amount_override(self):
        return self._get('ledger','amount_override')

    def set_session_type(self,text):
        self._set('ledger','session_type',text)

    def get_session_type(self):
        return self._get('ledger','session_type')

    def set_response_type(self,text):
        self._set('ledger','response_type',text)

    def get_response_type(self):
        return self._get('ledger','response_type')

    def set_user_logged_in(self, value):
        return self._set('ledger','user_logged_in',value)

    def get_user_logged_in(self):
        return self._get('ledger','user_logged_in')


def calculate_excl_gst(amount):
    TWELVEPLACES = D(10) ** -12
    getcontext().prec = 22
    result = (D(100.0) / D(100 + settings.LEDGER_GST) * D(amount)).quantize(TWELVEPLACES)
    return result


def createBasket(product_list, owner, system, vouchers=None, force_flush=True, booking_reference=None, booking_reference_link=None,organisation_id=None):
    ''' Create a basket so that a user can check it out.
        @param product_list - [
            {
                "id": "<id of the product in oscar>",
                "quantity": "<quantity of the products to be added>"
            }
        ]
        @param - owner (user id or user object)
    '''
    try:
        old_basket = basket = None
        valid_products = []
        User = get_user_model()
        # Check if owner is of class AUTH_USER_MODEL or id
        if not isinstance(owner, AnonymousUser):
            if not isinstance(owner, User):
                owner = User.objects.get(id=owner)
            # Check if owner has previous baskets
            if owner.baskets.filter(status='Open'):
                old_basket = owner.baskets.get(status='Open')

        # Use the previously open basket if its present or create a new one
        if old_basket:
            if system.lower() == old_basket.system.lower() or not old_basket.system:
                basket = old_basket
                if force_flush:
                    basket.flush()
            else:
                raise ValidationError('You have a basket that is not completed in system {}'.format(old_basket.system))
        else:
            basket = Basket()

        # Set the owner and strategy being used to create the basket
        if isinstance(owner, User):
            basket.owner = owner
        basket.system = system
        basket.booking_reference = booking_reference
        basket.booking_reference_link = booking_reference_link
        if organisation_id: 
            try:
               org_obj = Organisation.objects.get(id=organisation_id)
               basket.organisation = org_obj
            except:
               print ("Error retreiving Organisation.objects.get(id="+str(organisation_id)+")")
               raise ValidationError('Error with organisation id {}'.format(organisation_id))
        basket.strategy = selector.strategy(user=owner)
        # Check if there are products to be added to the cart and if they are valid products
        if not product_list:
            raise ValueError('There are no products to add to the order.')
        for product in product_list:
            p = Product.objects.get(id=product["id"])
            if not product.get("quantity"):
                product["quantity"] = 1
            valid_products.append({'product': p, 'quantity': product["quantity"]})
        # Add the valid products to the basket
        for p in valid_products:
            basket.add_product(p['product'],p['quantity'])
        # Add vouchers to the basket
        if vouchers is not None:
            for v in vouchers:
                basket.vouchers.add(Voucher.objects.get(code=v["code"]))
        # Save the basket
        basket.save()
        return basket
    except Product.DoesNotExist:
        raise
    except Exception as e:
        raise


def createCustomBasket(product_list, owner, system,vouchers=None, force_flush=True, booking_reference=None, booking_reference_link=None,organisation_id=None):
    ''' Create a basket so that a user can check it out.
        @param product_list - [
            {
                "id": "<id of the product in oscar>",
                "quantity": "<quantity of the products to be added>"
            }
        ]
        @param - owner (user id or user object)
    '''
    #import pdb; pdb.set_trace()
    try:
        old_basket = basket = None
        valid_products = []
        User = get_user_model()
        # Check if owner is of class AUTH_USER_MODEL or id
        if not isinstance(owner, AnonymousUser):
            if not isinstance(owner, User):
                owner = User.objects.get(id=owner)
            # Check if owner has previous baskets
            open_baskets = Basket.objects.filter(status='Open',system=system,owner=owner).count()
            if open_baskets > 0:
                old_basket = Basket.objects.filter(status='Open',system=system,owner=owner)[0]

        # Use the previously open basket if its present or create a new one
        if old_basket:
            if system.lower() == old_basket.system.lower() or not old_basket.system:
                basket = old_basket
                if force_flush:
                    basket.flush()
            else:
                raise ValidationError('You have a basket that is not completed in system {}'.format(old_basket.system))
        else:
            basket = Basket()
        # Set the owner and strategy being used to create the basket
        if isinstance(owner, User):
            basket.owner = owner
        basket.system = system
        basket.strategy = selector.strategy(user=owner)
        basket.booking_reference = booking_reference
        basket.booking_reference_link = booking_reference_link
        if organisation_id:
            try:
               org_obj = Organisation.objects.get(id=organisation_id)
               basket.organisation = org_obj
            except:
               print ("Error retreiving Organisation.objects.get(id="+str(organisation_id)+")")
               raise ValidationError('Error with organisation id {}'.format(organisation_id))
        basket.custom_ledger = True
        # Check if there are products to be added to the cart and if they are valid products
        # EXAMPLE config for settings.py: os.environ['LEDGER_CUSTOM_PRODUCT_LIST'] = "('ledger_description','quantity','price_incl_tax','price_excl_tax','oracle_code','line_status')"
        # you can import def calculate_excl_gst and use this funcation to calculate the mount with out gst on line items that have gst component.
        ledger_product_custom_fields = env('LEDGER_PRODUCT_CUSTOM_FIELDS', None)
        ledger_product_default_fields = ('ledger_description','quantity','price_incl_tax','oracle_code')

        UPDATE_PAYMENT_ALLOCATION = env('UPDATE_PAYMENT_ALLOCATION', False)
        if UPDATE_PAYMENT_ALLOCATION is True:
             ledger_product_default_fields = ('ledger_description','quantity','price_incl_tax','oracle_code','line_status')

        if ledger_product_custom_fields:
                ledger_product_default_fields = ledger_product_custom_fields

        for p in product_list:            
            if not all(d in p for d in ledger_product_default_fields):
                raise ValidationError('Please make sure that the product format is valid')

            if ledger_product_custom_fields:
                 if 'price_excl_tax' in ledger_product_custom_fields:
                     # dont calculate tax as this should be included in the product list
                     pass
                 else:
                     p['price_excl_tax'] = calculate_excl_gst(p['price_incl_tax'])
            else:
                 p['price_excl_tax'] = calculate_excl_gst(p['price_incl_tax'])
        # Save the basket
        basket.save()
        # Add the valid products to the basket
        for p in product_list:
            basket.addNonOscarProduct(p)
        # Save the basket (again)
        basket.save()
        # Add vouchers to the basket
        if vouchers is not None:
            for v in vouchers:
                basket.vouchers.add(Voucher.objects.get(code=v["code"]))
            basket.save()
        return basket
    except Product.DoesNotExist:
        raise
    except Exception as e:
        raise




def createCustomBasketv2(product_list, owner, system,vouchers=None, force_flush=True, booking_reference=None, booking_reference_link=None,organisation_id=None, ledger_product_custom_fields=None):
    ''' Create a basket so that a user can check it out.
        @param product_list - [
            {
                "id": "<id of the product in oscar>",
                "quantity": "<quantity of the products to be added>"
            }
        ]
        @param - owner (user id or user object)
    '''
    print ("HERE 1")
    #import pdb; pdb.set_trace()
    try:
        old_basket = basket = None
        valid_products = []
        User = get_user_model()
        # Check if owner is of class AUTH_USER_MODEL or id
        if not isinstance(owner, AnonymousUser):
            if not isinstance(owner, User):
                owner = User.objects.get(id=owner)
            # Check if owner has previous baskets
            open_baskets = Basket.objects.filter(status='Open',system=system,owner=owner).count()
            if open_baskets > 0:
                old_basket = Basket.objects.filter(status='Open',system=system,owner=owner)[0]

        # Use the previously open basket if its present or create a new one
        if old_basket:
            if system.lower() == old_basket.system.lower() or not old_basket.system:
                basket = old_basket
                if force_flush:
                    basket.flush()
            else:
                raise ValidationError('You have a basket that is not completed in system {}'.format(old_basket.system))
        else:
            basket = Basket()
        # Set the owner and strategy being used to create the basket
        if isinstance(owner, User):
            basket.owner = owner
        basket.system = system
        basket.strategy = selector.strategy(user=owner)
        basket.booking_reference = booking_reference
        basket.booking_reference_link = booking_reference_link
        if organisation_id:
            try:
               org_obj = Organisation.objects.get(id=organisation_id)
               basket.organisation = org_obj
            except:
               print ("Error retreiving Organisation.objects.get(id="+str(organisation_id)+")")
               raise ValidationError('Error with organisation id {}'.format(organisation_id))
        basket.custom_ledger = True
        # Check if there are products to be added to the cart and if they are valid products
        # EXAMPLE config for settings.py: os.environ['LEDGER_CUSTOM_PRODUCT_LIST'] = "('ledger_description','quantity','price_incl_tax','price_excl_tax','oracle_code','line_status')"
        # you can import def calculate_excl_gst and use this funcation to calculate the mount with out gst on line items that have gst component.
        #ledger_product_custom_fields = env('LEDGER_PRODUCT_CUSTOM_FIELDS', None)
        if ledger_product_custom_fields is None:
                ledger_product_custom_fields = ('ledger_description','quantity','price_incl_tax','oracle_code')

        #UPDATE_PAYMENT_ALLOCATION = env('UPDATE_PAYMENT_ALLOCATION', False)
        #if UPDATE_PAYMENT_ALLOCATION is True:
        #     ledger_product_default_fields = ('ledger_description','quantity','price_incl_tax','oracle_code','line_status')
      
        if ledger_product_custom_fields:
                ledger_product_default_fields = ledger_product_custom_fields

        for p in product_list:
            if not all(d in p for d in ledger_product_default_fields):                
                raise ValidationError('Please make sure that the product format is valid')
            if ledger_product_custom_fields:
                 if 'price_excl_tax' in ledger_product_custom_fields:
                     # dont calculate tax as this should be included in the product list
                     pass
                 else:
                     p['price_excl_tax'] = calculate_excl_gst(p['price_incl_tax'])
            else:
                 p['price_excl_tax'] = calculate_excl_gst(p['price_incl_tax'])
        # Save the basket
        basket.save()
        # Add the valid products to the basket
        for p in product_list:
            basket.addNonOscarProduct(p)
        # Save the basket (again)
        basket.save()
        # Add vouchers to the basket
        if vouchers is not None:
            for v in vouchers:
                basket.vouchers.add(Voucher.objects.get(code=v["code"]))
            basket.save()
        return basket
    except Product.DoesNotExist:
        raise
    except Exception as e:
        raise

