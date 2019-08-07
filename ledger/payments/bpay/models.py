from django.db import models, connection
from django.conf import settings
from decimal import Decimal as D
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
from oscar.apps.order.models import Order
import datetime

class BpayJobRecipient(models.Model):
    email = models.EmailField(unique=True)

    class Meta:
        db_table = 'payments_bpayjobrecipient'

    def __unicode__(self):
        return self.email

class BpayFile(models.Model):
    inserted = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(help_text='File Creation Date Time.')
    file_id = models.BigIntegerField(help_text='File Identification Number.')

    class Meta:
        unique_together = ('created','file_id')
        db_table = 'payments_bpayfile'
        
    def __unicode__(self):
        return 'File #{0} {1}'.format(self.file_id,self.created.strftime('%Y-%m-%d %H:%M:%S'))
    
    @property
    def items_validated(self):
        total_items = (self.credit_items + self.debit_items + self.cheque_items)
        return self.transactions.count() == total_items

class BpayFileTrailer(models.Model):
    total = models.DecimalField(default=0,decimal_places=2,max_digits=12)
    groups = models.IntegerField(default=0)
    records = models.IntegerField(default=0)
    file = models.OneToOneField(BpayFile, related_name='trailer')

    class Meta:
        db_table = 'payments_bpayfiletrailer'

@receiver(post_save, sender=BpayFileTrailer)
def update_file_view(sender, instance, **kwargs):
    try:
        cursor = connection.cursor()
        sql = 'CREATE OR REPLACE VIEW bpay_bpaycollection_v AS \
                select date(created), count(*), sum(a.credit_total) as credit_total, \
                sum(a.cheque_total) as cheque_total,sum(a.debit_total) as debit_total, \
                (sum(a.credit_total)+sum(a.cheque_total)+sum(a.debit_total)) as total from payments_bpayfile f\
                inner join \
                (select file_id,sum(credit_amount) as credit_total,sum(cheque_amount) as cheque_total,\
                sum(debit_amount) as debit_total from payments_bpayaccountrecord GROUP BY \
                file_id,credit_amount,cheque_amount,debit_amount) a \
                on f.id=a.file_id \
                group by date(f.created);'
        cursor.execute(sql)
    except Exception as e:
        raise ValidationError(e)

class BpayTransaction(models.Model):
    TRANSACTION_TYPE = (
        ('399', 'credit'),
        ('699', 'debit')
    )
    PAYMENT_INSTRUCTION_CODES = (
        ('05', 'payment'),
        ('15', 'error correction'),
        ('25', 'reversal')
    )
    PAYMENT_METHOD_CODES = (
        ('001', 'Debit Account'),
        ('101', 'Visa'),
        ('201', 'Mastercard'),
        ('301', 'Bankcard')
    )
    ENTRY_METHODS = (
        ('000','undefined'),
        ('001', 'key entry by operator'),
        ('002', 'touch tone entry by payer'),
        ('003', 'speech recognition'),
        ('004', 'internet/on-line banking'),
        ('005', 'electtronic bill presentment'),
        ('006', 'batch data entry'),
        ('007', 'mobile entry')
    )
    REF_REV_CODE = (
        ('001','payer paid twice'),
        ('002', 'payer paid wrong account'),
        ('003', 'payer paid wrong biller'),
        ('004', 'payer paid wrong amount'),
        ('005', 'payer did not authorise'),
        ('400', 'Visa chargeback'),
        ('500', 'MasterCard chargeback'),
        ('600', 'Bankcard chargeback')
    )
    created = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(decimal_places=2,max_digits=12)
    type = models.CharField(max_length=3,choices=TRANSACTION_TYPE, help_text='Indicates whether it is a credit or debit item',validators=[MinLengthValidator(3)],)
    cheque_num = models.IntegerField(default=0, help_text='Number of cheques in deposit')
    crn = models.CharField(max_length=20,help_text='Customer Referencer Number')
    original_crn = models.CharField(null=True,blank=True,max_length=20,help_text='Customer Referencer Number')
    txn_ref = models.CharField(max_length=21, help_text='Transaction Reference Number',validators=[MinLengthValidator(12)])
    service_code = models.CharField(max_length=7, help_text='Unique identification for a service provider realting to a bill.', validators=[MinLengthValidator(1)])
    p_instruction_code = models.CharField(max_length=2,choices=PAYMENT_INSTRUCTION_CODES, help_text='Payment instruction method.',validators=[MinLengthValidator(2)])
    p_method_code = models.CharField(max_length=3,choices=PAYMENT_METHOD_CODES, help_text='Method of payment.', validators=[MinLengthValidator(3)])
    p_date = models.DateTimeField(help_text='Date of payment.')
    entry_method = models.CharField(max_length=3, choices=ENTRY_METHODS, null=True, blank=True, help_text='Manner in which the payment details are captured.')
    orig_ref_num = models.CharField(max_length=21, blank=True, null=True, help_text='Contains the original/previous CRN in the case of a refund or reversal.')
    ref_rev_code = models.CharField(max_length=3,choices=REF_REV_CODE,blank=True,null=True, help_text='Reason code for reversal or refund.')
    discretionary_data = models.CharField(max_length=50, null=True, blank=True, help_text='Reason for refund or reversal.')
    payer_name = models.CharField(max_length=40, null=True, blank=True, help_text='Name of payer extracted from payer\'s account details.')
    country = models.CharField(max_length=3, null=True, blank=True, help_text='Country of payment.')
    state = models.CharField(max_length=4,null=True, blank=True, help_text='State code of payer institution.')
    car = models.CharField(max_length=20,null=True, blank=True, help_text='Customer Additional Reference.')
    discount_ref = models.CharField(max_length=20, null=True, blank=True, help_text='Discount Reference Code.')
    discount_method = models.CharField(max_length=3, null=True, blank=True, help_text='Discount Method Code.')
    biller_code = models.CharField(max_length=10)
    file = models.ForeignKey(BpayFile, related_name='transactions')

    class Meta:
        unique_together = ('crn', 'txn_ref', 'p_date')
        db_table = 'payments_bpaytransaction'

    @property
    def approved(self):
        if self.service_code == '0':
            return True
        return False

    @property
    def order(self):
        from ledger.payments.models import Invoice, InvoiceBPAY
        order = None
        try:
            order = Order.objects.get(number=Invoice.objects.get(reference=self.crn).order_number)
        except Order.DoesNotExist:
            pass
        except Invoice.DoesNotExist:
            pass
        
        if not order:
            try:    
                order = Order.objects.get(number=InvoiceBPAY.objects.get(bpay=self).invoice.order_number)
            except InvoiceBPAY.DoesNotExist:
                pass
        
        return order

    @property
    def payment_allocated(self):
        allocated = D('0.0')
        if self.order:
            lines = self.order.lines.all()
            for line in lines:
                for k,v in line.payment_details.items():
                    if k == 'bpay':
                        for i,a in v.items():
                            if i == str(self.id):
                                allocated += D(a)
        return allocated

    @property
    def refund_allocated(self):
        allocated = D('0.0')
        if self.order:
            lines = self.order.lines.all()
            for line in lines:
                for k,v in line.refund_details.items():
                    if k == 'bpay':
                        for i,a in v.items():
                            if i == str(self.id):
                                allocated += D(a)
        return allocated

    @property
    def system(self):
        pass
    
    @property
    def matched(self):
        from ledger.payments.invoice.models import Invoice, InvoiceBPAY
        matched = False
        
        # Check if there is any invoice with a matching crn
        try:
            Invoice.objects.get(reference=self.crn)
            matched = True
        except Invoice.DoesNotExist:
            pass
        
        # Check if there is any association between invoice and this payment
        if not matched:
            try:
                InvoiceBPAY.objects.get(bpay=self)
                matched = True
            except InvoiceBPAY.DoesNotExist:
                pass
        
        return matched
    
    @property
    def linked(self):
        from ledger.payments.invoice.models import InvoiceBPAY
        linked = False
        # Check if there is any association between invoice and this payment
        try:
            InvoiceBPAY.objects.get(bpay=self)
            linked = True
        except InvoiceBPAY.DoesNotExist:
            pass
        
        return linked

    def __unicode__(self):
        return str(self.crn)

class BpayGroupRecord(models.Model):
    DATE_MODIFIERS = (
        (1,'interim/previous day'),
        (2, 'final/previous day'),
        (3, 'interim/same day'),
        (4, 'final/same day')
    )
    settled = models.DateTimeField(help_text='File Settlement Date Time')
    modifier = models.IntegerField(choices=DATE_MODIFIERS, help_text='As of Date modifier')
    file = models.ForeignKey(BpayFile, related_name='group_records')

    class Meta:
        db_table = 'payments_bpaygrouprecord'

class BpayGroupTrailer(models.Model):
    total = models.DecimalField(default=0,decimal_places=2,max_digits=12)
    accounts = models.IntegerField(default=0)
    records = models.IntegerField(default=0)
    file = models.ForeignKey(BpayFile, related_name='group_trailerrecords')

    class Meta:
        db_table = 'payments_bpaygrouptrailer'

class BpayAccountRecord(models.Model):
    credit_items = models.IntegerField(default=0)
    credit_amount = models.DecimalField(default=0,decimal_places=2,max_digits=12)
    cheque_items = models.IntegerField(default=0)
    cheque_amount = models.DecimalField(default=0,decimal_places=2,max_digits=12)
    debit_amount =models.DecimalField(default=0,decimal_places=2,max_digits=12)
    debit_items = models.IntegerField(default=0)
    file = models.ForeignKey(BpayFile, related_name='account_records')

    class Meta:
        db_table = 'payments_bpayaccountrecord'

class BpayAccountTrailer(models.Model):
    total = models.DecimalField(default=0,decimal_places=2,max_digits=12)
    records = models.IntegerField(default=0)
    file = models.ForeignKey(BpayFile, related_name='account_trailerrecords')

    class Meta:
        db_table = 'payments_bpayaccounttrailer'

class BpayCollection(models.Model):
    date = models.DateField(primary_key=True)
    count = models.IntegerField()
    credit_total = models.DecimalField(max_digits=12,decimal_places=2)
    cheque_total = models.DecimalField(max_digits=12,decimal_places=2)
    debit_total = models.DecimalField(max_digits=12,decimal_places=2)
    total = models.DecimalField(max_digits=12,decimal_places=2)
    
    class Meta:
        managed = False
        db_table = 'bpay_bpaycollection_v'
        
    @property
    def files(self):
        return BpayFile.objects.filter(created__contains=self.date)
    
    @property
    def transactions(self):
        txns = []
        for f in self.files:
            txns.extend(f.transactions.all())
        return txns
    
class BillerCodeSystem(models.Model):
    biller_code = models.CharField(max_length=10,unique=True)
    system = models.CharField(max_length=100)

    class Meta:
        db_table = 'payments_billercodesystem'
    
    def __str__(self):
        return '{} - Biller Code: {}'.format(self.system,self.biller_code)
    
class BillerCodeRecipient(models.Model):
    app = models.ForeignKey(BillerCodeSystem, related_name='recipients')
    email = models.EmailField()
    
    class Meta:
        db_table = 'payments_billercoderecipient'
