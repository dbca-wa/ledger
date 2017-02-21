from django.db import models
from django.utils.translation import ugettext_lazy as _
from oscar.apps.order.abstract_models import AbstractLine as CoreAbstractLine

class Line(CoreAbstractLine):

    oracle_code = models.CharField("Oracle Code",max_length=50,null=True,blank=True)
    partner_name = models.CharField(
        _("Partner name"), max_length=128, blank=True,null=True)
    partner_sku = models.CharField(_("Partner SKU"), max_length=128,null=True)

    # A line reference is the ID that a partner uses to represent this
    # particular line (it's not the same as a SKU).
    partner_line_reference = models.CharField(
        _("Partner reference"), max_length=128, blank=True, null=True,
        help_text=_("This is the item number that the partner uses "
                    "within their system"))
    partner_line_notes = models.TextField(
        _("Partner Notes"), blank=True, null=True)

from oscar.apps.order.models import *  # noqa
