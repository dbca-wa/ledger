from __future__ import unicode_literals
import traceback
from django.db import models
from django.conf import settings
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
    parser = models.ForeignKey(OracleParser,related_name='invoices')
    reference = models.CharField(max_length=50)
    details = JSONField() 

def increment_receipt_number():
    last_interface = OracleInterface.objects.all().order_by('id').last()
    if not last_interface:
         return 80000
    receipt_no = last_interface.receipt_number
    new_receipt_no = receipt_no + 1
    return new_receipt_no

class OracleInterface(models.Model):
    receipt_number = models.IntegerField(null=True,blank=True,default=increment_receipt_number)
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


class OracleAccountCode(models.Model):
    active_receivables_activities = models.CharField(max_length=50,primary_key=True)
    description = models.CharField(max_length=240)    

    class Meta:
        managed = False
        db_table = 'payments_account_codes'

class OracleOpenPeriod(models.Model):
    period_name = models.CharField(max_length=240,primary_key=True)
    closing_status = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'payments_open_periods'

# Refund Tracking
class TrackRefund(models.Model):
    REFUND_TYPES = (
        (1,'Cash'),
        (2,'Bpoint'),
        (3,'Bpay')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    type = models.SmallIntegerField(choices=REFUND_TYPES)
    refund_id = models.PositiveIntegerField()
    details = models.TextField()
