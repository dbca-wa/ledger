from django.db import models
from oscar.apps.catalogue.abstract_models import AbstractProduct as CoreAbstractProduct

class Product(CoreAbstractProduct):
    
    oracle_code = models.CharField("Oracle Code",max_length=50,null=True,blank=True)
    system = models.CharField(max_length=4)

from oscar.apps.catalogue.models import *  # noqa
