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
        ('refund','refund')
    )
    
    invoice = models.ForeignKey(Invoice, related_name='cash_transactions', to_field='reference')
    amount = models.DecimalField(decimal_places=2,max_digits=12)
    created = models.DateTimeField(auto_now_add=True)
    original_txn = models.ForeignKey('self', null=True, blank=True)
    type = models.CharField(choices=TRANSACTION_TYPES, max_length=7)
    
    def save(self, *args, **kwargs):
        if self.invoice.payment_status == 'paid':
            raise ValidationError('This invoice has already been paid for.')
        if decimal.Decimal(self.amount) > self.invoice.balance:
            raise ValidationError('The amount to be charged is more than the amount payable for this invoice.')

        super(CashTransaction, self).save(*args, **kwargs)
    
    def clean(self):
        if self.type in ['reversal','refund'] and not self.orig_txn:
            raise ValidationError("This transaction type requires a previous transaction.")
        
