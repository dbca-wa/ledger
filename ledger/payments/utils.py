import requests
import json
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
#
from ledger.basket.models import Basket
from ledger.catalogue.models import Product
from oscar.core.loading import get_class

OrderPlacementMixin = get_class('checkout.mixins','OrderPlacementMixin')
Selector = get_class('partner.strategy', 'Selector')
selector = Selector()

def checkSystem(system_id):
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

def createBasket(product_list,owner,system,force_flush=True):
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
        if not checkSystem(system):
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
            print old_basket.system
            if system == old_basket.system or not old_basket.system:
                basket = old_basket
                if force_flush:
                    basket.flush()
            else:
                raise ValidationError('You have a basket that is not completed in this application {}'.format(old_basket.system))
        else:
            basket = Basket()
        # Set the owner and strategy being used to create the basket    
        basket.owner = owner
        basket.system = system
        basket.strategy = selector.strategy(user=owner)
        # Check if there are products to be added to the cart and if they are valid products
        if not product_list:
            raise ValueError('There are no products to add to the order.')
        product_dict_list = json.loads(product_list)
        for product in product_dict_list:
            p = Product.objects.get(id=product["id"])
            if not product.get("quantity"):
                product["quantity"] = 1
            valid_products.append({'product': p, 'quantity': product["quantity"]})
        # Add the valid products to the basket
        for p in valid_products:
            basket.add_product(p['product'],p['quantity'])
        # Save the basket
        basket.save()
        return basket
    except Product.DoesNotExist:
        raise
    except Exception as e:
        raise