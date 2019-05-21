import json
from decimal import Decimal as D
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField
from oscar.apps.order.abstract_models import AbstractLine as CoreAbstractLine

class Line(CoreAbstractLine):

    def get_default_data():
        return { 
        'bpay': {}, 
        'cash': {}, 
        'card': {}
        }

    oracle_code = models.CharField("Oracle Code",max_length=50,null=True,blank=True)
    partner_name = models.CharField(
        _("Partner name"), max_length=128, blank=True,null=True)
    partner_sku = models.CharField(_("Partner SKU"), max_length=128,null=True)
    payment_details = JSONField(db_index=True,default=get_default_data)
    refund_details = JSONField(db_index=True,default=get_default_data)
    deduction_details = JSONField(db_index=True,default=get_default_data)

    @property
    def paid(self):
        amount = D(0.0)
        for k,v in self.payment_details.items():
            for i,a in v.items():
                amount += D(a)
        return amount

    @property
    def refunded(self):
        amount = D(0.0)
        for k,v in self.refund_details.items():
            for i,a in v.items():
                amount += D(a)
        return amount

    @property
    def deducted(self):
        amount = D(0.0)
        for k,v in self.deduction_details.items():
            for i,a in v.items():
                amount += D(a)
        return amount

    # A line reference is the ID that a partner uses to represent this
    # particular line (it's not the same as a SKU).
    partner_line_reference = models.CharField(
        _("Partner reference"), max_length=128, blank=True, null=True,
        help_text=_("This is the item number that the partner uses "
                    "within their system"))
    partner_line_notes = models.TextField(
        _("Partner Notes"), blank=True, null=True)

from oscar.apps.order.models import *  # noqa
