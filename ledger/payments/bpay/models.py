from django.db import models, connection
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.encoding import python_2_unicode_compatible
from django.core.validators import MinLengthValidator
from django.core.exceptions import ValidationError
import datetime

class BpayFile(models.Model):
    DATE_MODIFIERS = (
        (1,'interim/previous day'),
        (2, 'final/previous day'),
        (3, 'interim/same day'),
        (4, 'final/same day')
    )
    inserted = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(help_text='File Creation Date Time.')
    file_id = models.BigIntegerField(help_text='File Identification Number.')
    settled = models.DateTimeField(help_text='File Settlement Date Time')
    date_modifier = models.IntegerField(choices=DATE_MODIFIERS, help_text='As of Date modifier')
    credit_items = models.IntegerField(default=0)
    credit_amount = models.DecimalField(default=0,decimal_places=2,max_digits=12)
    cheque_items = models.IntegerField(default=0)
    cheque_amount =models.DecimalField(default=0,decimal_places=2,max_digits=12)
    debit_amount =models.DecimalField(default=0,decimal_places=2,max_digits=12)
    debit_items = models.IntegerField(default=0)
    account_total = models.DecimalField(default=0,decimal_places=2,max_digits=12)
    account_records = models.IntegerField(default=0)
    group_total = models.DecimalField(default=0,decimal_places=2,max_digits=12)
    group_accounts = models.IntegerField(default=0)
    group_records = models.IntegerField(default=0)
    file_total = models.DecimalField(default=0,decimal_places=2,max_digits=12)
    file_groups = models.IntegerField(default=0)
    file_records = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('created','file_id')
        
    def __unicode__(self):
        return 'File #{0} {1}'.format(self.file_id,self.created.strftime('%Y-%m-%d %H:%M:%S'))
    
    @property
    def items_validated(self):
        total_items = (self.credit_items + self.debit_items + self.cheque_items)
        return self.transactions.count() == total_items
    
@receiver(post_save, sender=BpayFile)
def update_file_view(sender, instance, **kwargs):
    try:
        cursor = connection.cursor()
        cursor.execute('CREATE OR REPLACE VIEW dpaw_payments_bpaycollection_v AS SELECT date(created),\
                       count(*),sum(credit_amount) AS credit_total\
                       , sum(cheque_amount) as cheque_total, sum(debit_amount) as debit_total,sum(file_total) as total  from dpaw_payments_bpayfile GROUP BY date(created)')
    except Exception as e:
        connection.rollback()
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
    crn = models.BigIntegerField(help_text='Customer Referencer Number')
    txn_ref = models.CharField(max_length=21, help_text='Transaction Reference Number',validators=[MinLengthValidator(12)])
    service_code = models.CharField(max_length=7, help_text='Unique identification for a service provider realting to a bill.', validators=[MinLengthValidator(1)])
    p_instruction_code = models.CharField(max_length=2,choices=PAYMENT_INSTRUCTION_CODES, help_text='Payment instruction method.',validators=[MinLengthValidator(2)])
    p_method_code = models.CharField(max_length=3,choices=PAYMENT_METHOD_CODES, help_text='Method of payment.', validators=[MinLengthValidator(3)])
    p_date = models.DateTimeField(help_text='Date of payment.')
    entry_method = models.CharField(max_length=3, choices=ENTRY_METHODS, null=True, blank=True, help_text='Manner in which the payment details are captured.')
    orig_ref_num = models.CharField(max_length=21, blank=True, null=True, help_text='Contains the original/previous CRN in the case of a refund or reversal.')
    ref_rev_code = models.CharField(max_length=3,choices=REF_REV_CODE,blank=True,null=True, help_text='Reason code for reversal or refund.')
    discretionary_data = models.CharField(max_length=50, null=True, blank=False, help_text='Reason for refund or reversal.')
    payer_name = models.CharField(max_length=40, null=True, blank=True, help_text='Name of payer extracted from payer\'s account details.')
    country = models.CharField(max_length=3, null=True, blank=False, help_text='Country of payment.')
    state = models.CharField(max_length=4,null=True, blank=True, help_text='State code of payer institution.')
    car = models.CharField(max_length=20,null=True, blank=False, help_text='Customer Additional Reference.')
    discount_ref = models.CharField(max_length=20, null=True, blank=True, help_text='Discount Reference Code.')
    discount_method = models.CharField(max_length=3, null=True, blank=True, help_text='Discount Method Code.')
    file = models.ForeignKey(BpayFile, related_name='transactions')

    class Meta:
        unique_together = ('crn', 'txn_ref', 'p_date')
        
    @property
    def system(self):
        pass

    def __unicode__(self):
        return str(self.crn)
    
class BpayCollection(models.Model):
    date = models.DateField(primary_key=True)
    count = models.IntegerField()
    credit_total = models.DecimalField(max_digits=12,decimal_places=2)
    cheque_total = models.DecimalField(max_digits=12,decimal_places=2)
    debit_total = models.DecimalField(max_digits=12,decimal_places=2)
    total = models.DecimalField(max_digits=12,decimal_places=2)
    
    class Meta:
        managed = False
        db_table = 'dpaw_payments_bpaycollection_v'
        
    @property
    def files(self):
        return BpayFile.objects.filter(created__contains=self.date)
    
    @property
    def transactions(self):
        txns = []
        for f in self.files:
            txns.extend(f.transactions.all())
        return txns