from django.db import models
from oscar.apps.basket.abstract_models import AbstractBasket as CoreAbstractBasket

class Basket(CoreAbstractBasket):
    system = models.CharField(max_length=4,blank=True,null=False)

from oscar.apps.basket.models import *  # noqa
