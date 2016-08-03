from django.db import models
from oscar.apps.order.abstract_models import AbstractLine as CoreAbstractLine

class Line(CoreAbstractLine):

    oracle_code = models.CharField("Oracle Code",max_length=50,null=True,blank=True)

from oscar.apps.order.models import *  # noqa
