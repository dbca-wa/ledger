import json
from django.views import generic
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.shortcuts import get_object_or_404
#
from oscar.apps.basket.models import Basket
from oscar.apps.catalogue.models import Product
from oscar.core.loading import get_class
#
from models import Invoice

OrderPlacementMixin = get_class('checkout.mixins','OrderPlacementMixin')
Selector = get_class('partner.strategy', 'Selector')
selector = Selector()

def createBasket(product_list,owner,force_flush=True):
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
        if not isinstance(owner,User):
            owner = User.objects.get(id=owner)
            
        # Check if owner has previous baskets
        if owner.baskets.filter(status='Open'):
            old_basket = owner.baskets.get(status='Open')

        # Use the previously open basket if its present or create a new one    
        if old_basket:
            basket = old_basket
            if force_flush:
                basket.flush()
        else:
            basket = Basket()
        # Set the owner and strategy being used to create the basket    
        basket.owner = owner
        basket.strategy = selector.strategy(user=owner)
        
        # Check if there are products to be added to the cart and if they are valid products
        if not product_list:
            raise ValueError('There are no products to add to the order.')
        product_dict_list = json.loads(product_list)
        for product in product_dict_list:
            p = Product.objects.get(id=product["id"])
            if not product["quantity"]:
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
        raise str(e)

class InvoiceDetailView(generic.DetailView):
    model = Invoice
    template_name = 'dpaw_payments/invoice/invoice.html'
    context_object_name = 'invoice'

    def get_object(self):
        invoice = get_object_or_404(Invoice, reference=self.kwargs['reference'])
        return invoice

class PaymentErrorView(generic.TemplateView):
    template_name = 'dpaw_payments/payment_error.html'

class InvoiceSearchView(generic.TemplateView):

    template_name = 'dpaw_payments/invoice/invoice_search.html'
    
class InvoicePaymentView(generic.TemplateView):

    template_name = 'dpaw_payments/invoice/payment.html'

    def get_context_data(self, **kwargs):
        ctx = super(InvoicePaymentView, self).get_context_data(**kwargs)
        if self.request.GET.get('amountProvided') == 'true':
            ctx['amountProvided'] = True

        return ctx