from __future__ import unicode_literals
import traceback
from django.db import models
from django.contrib.postgres.fields import JSONField
from ledger.payments.bpay.models import BpayTransaction, BpayFile, BillerCodeRecipient, BillerCodeSystem
from ledger.payments.invoice.models import Invoice, InvoiceBPAY
from ledger.payments.bpoint.models import BpointTransaction, BpointToken
from ledger.payments.cash.models import CashTransaction

class OracleParser(models.Model):
    inserted = models.DateTimeField(auto_now_add=True)
    date_parsed = models.DateField()

class OracleParserInvoice(models.Model):
    parser = models.ForeignKey(OracleParser)
    reference = models.CharField(max_length=50)
    details = JSONField() 
