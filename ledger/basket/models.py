from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from oscar.apps.basket.abstract_models import AbstractBasket as CoreAbstractBasket, AbstractLine as CoreAbstractLine
from oscar.models.fields.slugfield import SlugField
from ledger.catalogue.models import Product

class Basket(CoreAbstractBasket):
    system = models.CharField(max_length=4)
    custom_ledger = models.BooleanField(default=False)

    def all_lines(self):
        """
        Return a cached set of basket lines.
        This is important for offers as they alter the line models and you
        don't want to reload them from the DB as that information would be
        lost.
        """
        if self.id is None:
            return self.lines.none()
        if self._lines is None:
            if self.custom_ledger:
                self._lines = (self.lines.prefetch_related('attributes').order_by(self._meta.pk.name))
            else:
                self._lines = (self.lines.select_related('product', 'stockrecord').prefetch_related('attributes', 'product__images').order_by(self._meta.pk.name))
        return self._lines

    def addNonOscarProduct(self,data):
        ''' Used to add a nwew line item to a basket without
            using a product in oscar tables
            @param data - Basket Line Dict
        '''

        if not data.get('quantity'):
            data['quantity'] = 1 
        line = self.lines.create(**data)
        return line

    def is_shipping_required(self):
        """
        Test whether the basket contains physical products that require
        shipping.
        """
        if not self.custom_ledger:
            for line in self.all_lines():
                if line.product.is_shipping_required:
                    return True
        return False

@python_2_unicode_compatible
class Line(CoreAbstractLine):

    LINE_STATUS = (
        (1, 'New'),
        (2, 'Existing'),
        (3, 'Removed')
    )

    basket = models.ForeignKey(Basket,on_delete=models.CASCADE,related_name='lines',verbose_name=_("Basket"))
    product = models.ForeignKey(Product, related_name='basket_lines', on_delete=models.SET_NULL, verbose_name='Product', blank=True, null=True)
    stockrecord = models.ForeignKey('partner.StockRecord', on_delete=models.SET_NULL,related_name='basket_lines',blank=True, null=True)
    line_reference = SlugField(_("Line Reference"), max_length=128, db_index=True,blank=True,null=True)
    ledger_description = models.TextField(blank=True,null=True)
    oracle_code = models.CharField("Oracle Code",max_length=50,null=True,blank=True)
    price_excl_tax = models.DecimalField(_('Price excl. Tax'), decimal_places=12, max_digits=22,null=True)
    line_status = models.SmallIntegerField(choices=LINE_STATUS, default=1, null=True)


    def __str__(self):
        return _(
            u"Basket #%(basket_id)d, Product #%(product_id)s, quantity"
            u" %(quantity)d") % {'basket_id': self.basket.pk,
                                 'product_id': self.product.pk if self.product else None,
                                 'quantity': self.quantity}

    @property
    def purchase_info(self):
        """
        Return the stock/price info
        """
        if not self.basket.custom_ledger:
            if not hasattr(self, '_info'):
                # Cache the PurchaseInfo instance.
                self._info = self.basket.strategy.fetch_for_line(
                    self, self.stockrecord)
            return self._info
        else:
            #return None
            info = lambda: None
            info.price = lambda: None
            info.price.excl_tax = self.price_excl_tax
            info.price.incl_tax =  self.price_incl_tax
            info.price.tax = (self.price_incl_tax - self.price_excl_tax)
            info.price.is_tax_known = True 

            self._info = info
            return self._info

    @property
    def is_tax_known(self):
        return self.purchase_info.price.is_tax_known if self.purchase_info else (True if self.unit_tax else False)

    @property
    def unit_effective_price(self):
        """
        The price to use for offer calculations
        """
        return self.purchase_info.price.effective_price

    @property
    def unit_price_excl_tax(self):
        return self.purchase_info.price.excl_tax if self.purchase_info else self.price_excl_tax

    @property
    def unit_price_incl_tax(self):
        return self.purchase_info.price.incl_tax if self.purchase_info else self.price_incl_tax

    @property
    def unit_tax(self):
        return self.purchase_info.price.tax if self.purchase_info else (self.price_incl_tax - self.price_excl_tax)

from oscar.apps.basket.models import *  # noqa
