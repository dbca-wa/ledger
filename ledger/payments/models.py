from __future__ import unicode_literals
import traceback
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings
from django.contrib.postgres.fields import JSONField, IntegerRangeField
from ledger.payments.bpay.models import BpayTransaction, BpayFile, BillerCodeRecipient, BillerCodeSystem,BpayJobRecipient
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
    last_interface = OracleInterface.objects.values('id', 'receipt_number').order_by('-id').first()
    if not last_interface:
         return settings.ORACLE_IMPORT_SEQUENCE
    receipt_no = last_interface['receipt_number']
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
    source = models.CharField(max_length=30)
    method = models.CharField(max_length=30)

class OracleInterfaceSystem(models.Model):

    INTEGRATION_TYPE = (
                        ("no_api", "NO API"),
                        ("bpoint_api", "BPOINT API")
    )

    ORACLE_CALCULATION = (
                           ("version_1", "Version 1"),
                           ("version_2", "Version 2")
                         )

    system_id = models.CharField(max_length=10)
    system_name = models.CharField(max_length=128)
    enabled = models.BooleanField(default=False)
    deduct_percentage = models.BooleanField(default=False)
    source = models.CharField(max_length=30)
    method = models.CharField(max_length=30)
    integration_type = models.CharField(max_length=20, choices=INTEGRATION_TYPE, default='no_api', null=True,blank=True)
    oracle_calculation = models.CharField(max_length=20, choices=ORACLE_CALCULATION, default='version_1', null=True,blank=True)
    # specific for bpoint
    bpoint_currency = models.CharField(max_length=5, default="AUD", null=True,blank=True)
    bpoint_biller_code = models.CharField(max_length=256, default="", null=True,blank=True)
    bpoint_username = models.CharField(max_length=256, default="", null=True,blank=True)
    bpoint_password = models.CharField(max_length=256, default="", null=True,blank=True)
    bpoint_merchant_num = models.CharField(max_length=256, default="", null=True,blank=True)
    bpoint_test = models.NullBooleanField(default=True) 
    # sage configuration will need to be created below.


    def __str__(self):
        return '{} - {}'.format(self.system_name, self.system_id)

class OracleInterfaceDeduction(models.Model):
    oisystem = models.ForeignKey(OracleInterfaceSystem, related_name='deductions')
    percentage = models.PositiveIntegerField(validators=[MaxValueValidator(99), MinValueValidator(0)],null=True,blank=True)
    percentage_account_code = models.CharField(max_length=50,null=True,blank=True)
    destination_account_code = models.CharField(max_length=50,null=True,blank=True)

    class Meta:
        unique_together = ('oisystem', 'percentage_account_code', 'destination_account_code')

    def __str__(self):
        return '{} - {}'.format(self.oisystem, self.destination_account_code)

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
    _DATABASE = "oracle_finance"
    period_name = models.CharField(max_length=240,primary_key=True)
    closing_status = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = 'payments_open_periods'

class OracleFinanceDBRouter(object):

    def db_for_read(self, model, **hints):
       if model._meta.db_table == 'payments_open_periods' or model._meta.db_table == 'payments_account_codes':
           return 'oracle_finance'
       return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        return None

#     def db_for_read(self, model, **hints):
#         if model._meta.app_label == 'oracle_finance':
#             return 'oracle_finance'
#         return 'default'
#     
#     def db_for_write(self, model, **hints):
#         if model._meta.app_label == 'oracle_finance':
#             return 'oracle_finance'
#         return 'default'


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

class LinkedInvoiceGroupIncrementer(models.Model):
      system_identifier = models.ForeignKey(OracleInterfaceSystem)
      created = models.DateTimeField(auto_now_add=True)

class LinkedInvoice(models.Model):
    invoice_reference = models.CharField(max_length=1000) 
    system_identifier = models.ForeignKey(OracleInterfaceSystem)
    booking_reference = models.CharField(max_length=1000)
    booking_reference_linked = models.CharField(max_length=1000, null=True,blank=True)
    invoice_group_id = models.ForeignKey(LinkedInvoiceGroupIncrementer)
    created = models.DateTimeField(auto_now_add=True)
