from django.db import models
from oscar.apps.basket.abstract_models import AbstractBasket as CoreAbstractBasket, AbstractLine as CoreAbstractLine

class Basket(CoreAbstractBasket):
    system = models.CharField(max_length=4)

class Line(CoreAbstractLine):
    product = models.ForeignKey('catalogue.Product', related_name='basket_lines', on_delete=models.SET_NULL, verbose_name='Product', blank=True, null=True)

    def __str__(self):
        return _(
            u"Basket #%(basket_id)d, Product #%(product_id)d, quantity"
            u" %(quantity)d") % {'basket_id': self.basket.pk,
                                 'product_id': self.product.pk if self.product else None,
                                 'quantity': self.quantity}

from oscar.apps.basket.models import *  # noqa
