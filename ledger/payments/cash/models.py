from __future__ import unicode_literals
import decimal
from django.db import models
from django.core.exceptions import ValidationError
from ledger.payments.bpoint import settings as bpoint_settings
from django.utils.encoding import python_2_unicode_compatible
from ledger.payments.invoice.models import Invoice

class CashTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('payment','payment'),
        ('refund','refund'),
        ('reversal','reversal')
    )
    SOURCE_TYPES = (
        ('cash','cash'),
        ('cheque', 'cheque'),
        ('eft','eft'),
        ('money_order','money_order')
    )
    invoice = models.ForeignKey(Invoice, related_name='cash_transactions', to_field='reference')
    amount = models.DecimalField(decimal_places=2,max_digits=12)
    created = models.DateTimeField(auto_now_add=True)
    original_txn = models.ForeignKey('self', null=True, blank=True)
    type = models.CharField(choices=TRANSACTION_TYPES, max_length=8)
    source = models.CharField(choices=SOURCE_TYPES, max_length=11)
    collection_point = models.TextField()
    external = models.BooleanField(default=False)
    receipt = models.CharField(max_length=128,null=True,blank=True)

    def save(self, *args, **kwargs):
        # Validations
        self.ledger_validations()

        super(CashTransaction, self).save(*args, **kwargs)

    def ledger_validations(self):
        if not self.receipt and self.external:
            raise ValidationError("A receipt number is required for an external payment.ie receipt")
        if not self.collection_point and self.external:
            raise ValidationError("A collection point is required for an external payment.ie collection_point")
        if self.type in ['reversal','refund'] and self.invoice.payment_status == 'unpaid':
            raise ValidationError("A {} cannot be made for an unpaid invoice.".format(self.type))
        if self.type == 'refund' and (self.invoice.payment_amount < decimal.Decimal(self.amount)):
            raise ValidationError("A refund greater than the amount paid for the invoice cannot be made.")
        if self.invoice.payment_status == 'paid' and self.type == 'payment':
            raise ValidationError('This invoice has already been paid for.')
        if (decimal.Decimal(self.amount) > self.invoice.balance) and self.type == 'payment':
            raise ValidationError('The amount to be charged is more than the amount payable for this invoice.')
        if not self.external and not self.collection_point:
            self.collection_point = 'Kensington'