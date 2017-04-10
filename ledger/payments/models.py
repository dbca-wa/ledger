from __future__ import unicode_literals
import traceback
from django.db import models
from django.contrib.postgres.fields import JSONField
from ledger.payments.bpay.models import BpayTransaction, BpayFile, BillerCodeRecipient, BillerCodeSystem
from ledger.payments.invoice.models import Invoice, InvoiceBPAY
from ledger.payments.bpoint.models import BpointTransaction, BpointToken
from ledger.payments.cash.models import CashTransaction

# Oracle Integration
# ======================================
class OracleParser(models.Model):
    inserted = models.DateTimeField(auto_now_add=True)
    date_parsed = models.DateField()

    def __str__(self):
        return str(self.date_parsed)

class OracleParserInvoice(models.Model):
    parser = models.ForeignKey(OracleParser)
    reference = models.CharField(max_length=50)
    details = JSONField() 

class OracleInterface(models.Model):
    receipt_number = models.IntegerField()
    receipt_date = models.DateField()
    activity_name = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    customer_name = models.CharField(max_length=128)
    description = models.TextField()
    comments = models.TextField()
    status = models.CharField(max_length=15)
    line_item = models.TextField(blank=True,null=True)
    status_date = models.DateField()

class OracleInterfaceSystem(models.Model):
    system_id = models.CharField(max_length=10)
    system_name = models.CharField(max_length=128)

    def __str__(self):
        return '{} - {}'.format(self.system_name, self.system_id)

class OracleInterfaceRecipient(models.Model):
    system = models.ForeignKey(OracleInterfaceSystem,related_name='recipients')
    email = models.EmailField()

    def __str__(self):
        return '{} - {}'.format(str(self.system),self.email)
