import requests
import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.urlresolvers import resolve
from six.moves.urllib.parse import urlparse
#
from ledger.basket.models import Basket
from ledger.catalogue.models import Product
from oscar.core.loading import get_class
from oscar.apps.voucher.models import Voucher

OrderPlacementMixin = get_class('checkout.mixins','OrderPlacementMixin')
Selector = get_class('partner.strategy', 'Selector')
selector = Selector()

def isLedgerURL(url):
    ''' Check if the url is a ledger url
    :return: Boolean
    '''
    match = None
    try:
        match = resolve(urlparse(url)[2])
    except:
        pass
    if match:
        return True
    return False

def checkURL(url):
    try:
        resp = requests.get(url)
        resp.raise_for_status()
    except:
        raise

def systemid_check(system):
    system = system[1:]
    if len(system) == 3:
        system = '0{}'.format(system)
    elif len(system) > 4:
        system = system[:4]
    return system

def validSystem(system_id):
    ''' Check if the system is in the itsystems register.
    :return: Boolean
    '''
    res = requests.get('{}?system_id={}'.format(settings.CMS_URL,system_id), auth=(settings.LEDGER_USER,settings.LEDGER_PASS))
    try:
        res.raise_for_status()
        res = json.loads(res.content).get('objects')
        if not res:
            return False
        return True
    except:
        raise

def createBasket(product_list,owner,system,vouchers=None,force_flush=True):
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
        if not validSystem(system):
            raise ValidationError('A system with the given id does not exist.')
        old_basket = basket = None
        valid_products = []
        User = get_user_model()
        # Check if owner is of class AUTH_USER_MODEL or id
        if not isinstance(owner,User):
            owner = User.objects.get(id=owner)
        # Check if owner has previous baskets
        if owner.baskets.filter(status='Open'):
            old_basket = owner.baskets.get(status='Open')
        # Use the previously open basket if its present or create a new one    
        if old_basket:
            if system == old_basket.system or not old_basket.system:
                basket = old_basket
                if force_flush:
                    basket.flush()
            else:
                raise ValidationError('You have a basket that is not completed in system {}'.format(old_basket.system))
        else:
            basket = Basket()
        # Set the owner and strategy being used to create the basket    
        basket.owner = owner
        basket.system = system
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

def createCustomBasket(product_list,owner,system,vouchers=None,force_flush=True):
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
        if not validSystem(system):
            raise ValidationError('A system with the given id does not exist.')
        old_basket = basket = None
        valid_products = []
        User = get_user_model()
        # Check if owner is of class AUTH_USER_MODEL or id
        if not isinstance(owner,User):
            owner = User.objects.get(id=owner)
        # Check if owner has previous baskets
        if owner.baskets.filter(status='Open'):
            old_basket = owner.baskets.get(status='Open')
        # Use the previously open basket if its present or create a new one    
        if old_basket:
            if system == old_basket.system or not old_basket.system:
                basket = old_basket
                if force_flush:
                    basket.flush()
            else:
                raise ValidationError('You have a basket that is not completed in system {}'.format(old_basket.system))
        else:
            basket = Basket()
        # Set the owner and strategy being used to create the basket    
        basket.owner = owner
        basket.system = system
        basket.strategy = selector.strategy(user=owner)
        basket.custom_ledger = True
        # Check if there are products to be added to the cart and if they are valid products
        defaults = ('ledger_description','quantity','price_excl_tax','price_incl_tax','oracle_code')
        for p in product_list:
            if not all(d in p for d in defaults):
                raise ValidationError('Please make sure that the product format is valid')
        # Save the basket
        basket.save()
        # Add the valid products to the basket
        for p in product_list:
            basket.addNonOscarProduct(p)
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
