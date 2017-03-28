from __future__ import unicode_literals
import traceback
import decimal
from django.db import models
from django.db.models import Q 
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible
from django.core.exceptions import ValidationError
from oscar.apps.order.models import Order
from ledger.payments.bpay.crn import getCRN
from ledger.payments.bpay.models import BpayTransaction
from ledger.payments.bpoint.models import BpointTransaction, TempBankCard, BpointToken, UsedBpointToken

class Invoice(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(null=True,blank=True)
    amount = models.DecimalField(decimal_places=2,max_digits=12)
    order_number = models.CharField(max_length=50,unique=True)
    reference = models.CharField(max_length=50, unique=True)
    system = models.CharField(max_length=4,blank=True,null=True)
    token = models.CharField(max_length=80,null=True,blank=True)
    voided = models.BooleanField(default=False)

    def __unicode__(self):
        return 'Invoice #{0}'.format(self.reference)

    class Meta:
        app_label = 'payments'
        db_table = 'invoice_invoice'

    # Properties
    # =============================================
    @property
    def biller_code(self):
        ''' Return the biller code for bpay.
        '''
        return settings.BPAY_BILLER_CODE

    @property
    def order(self):
        ''' Get order matched to this invoice.
        '''
        try:
            return Order.objects.get(number=self.order_number)
        except Order.DoesNotExist:
            return None

    @property
    def number(self):
        length = len(str(self.id))
        val = '0'
        return '{}{}'.format((val*(6-length)),self.id)

    @property
    def owner(self):
        if self.order:
            return self.order.user
        return None

    @property
    def refundable_amount(self):
        return self.payment_amount - self.__calculate_total_refunds()

    @property
    def refundable(self):
        if self.refundable_amount > 0:
            return True
        return False

    @property
    def num_items(self):
        ''' Get the number of items in this invoice.
        '''
        return self.order.num_items

    @property
    def shipping_required(self):
        return self.order.basket.is_shipping_required() if self.order else False
    
    @property
    def linked_bpay_transactions(self):
        linked = InvoiceBPAY.objects.filter(invoice=self).values('bpay')
        txns = BpayTransaction.objects.filter(id__in=linked)
        return txns

    @property
    def bpay_transactions(self):
        ''' Get this invoice's bpay transactions.
        '''
        txns = BpayTransaction.objects.filter(crn=self.reference)
        linked_txns = BpayTransaction.objects.filter(id__in=InvoiceBPAY.objects.filter(invoice=self).values('bpay'))
        
        return txns | linked_txns

    @property
    def bpoint_transactions(self):
        ''' Get this invoice's bpoint transactions.
        '''
        return BpointTransaction.objects.filter(crn1=self.reference)

    @property
    def payment_amount(self):
        ''' Total amount paid from bpay,bpoint and cash.
        '''
        return self.__calculate_bpay_payments() + self.__calculate_bpoint_payments() + self.__calculate_cash_payments()

    @property
    def balance(self):
        amount = decimal.Decimal(self.amount - self.payment_amount)
        if amount < 0:
            amount =  decimal.Decimal(0)
        return amount

    @property
    def payment_status(self):
        ''' Payment status of the invoice.
        '''
        amount_paid = self.__calculate_bpay_payments() + self.__calculate_bpoint_payments() + self.__calculate_cash_payments()

        if amount_paid == decimal.Decimal('0') and self.amount > 0:
            return 'unpaid'
        elif amount_paid < self.amount:
            return 'partially_paid'
        elif amount_paid == self.amount:
            return 'paid'
        else:
            return 'over_paid'

    @property
    def single_card_payment(self):
        card = self.bpoint_transactions.count()
        bpay = self.bpay_transactions
        cash = self.cash_transactions
    
        if bpay or cash:
            return False
        
        if card > 1:
            return False
        return True

    @property
    def refundable_cards(self):
        cards = []
        refunds = self.bpoint_transactions.filter(Q(action='payment') | Q(action='capture'),dvtoken__isnull=False)
        for r in refunds:
            if r.refundable_amount > 0:
                cards.append(r)
        print cards
        return cards
        

    # Helper Functions
    # =============================================
    def __calculate_cash_payments(self):
        ''' Calcluate the amount of cash payments made
            less the reversals for this invoice.
        '''
        payments = dict(self.cash_transactions.filter(type='payment').aggregate(amount__sum=Coalesce(Sum('amount'), decimal.Decimal('0')))).get('amount__sum')
        reversals = dict(self.cash_transactions.filter(type='reversal').aggregate(amount__sum=Coalesce(Sum('amount'), decimal.Decimal('0')))).get('amount__sum')

        return payments - reversals

    def __calculate_bpoint_payments(self):
        ''' Calcluate the total amount of bpoint payments and
            captures made less the reversals for this invoice.
        '''
        payments = reversals = 0 
        payments = payments + dict(self.bpoint_transactions.filter(action='payment', response_code='0').aggregate(amount__sum=Coalesce(Sum('amount'), decimal.Decimal('0')))).get('amount__sum')
        payments = payments + dict(self.bpoint_transactions.filter(action='capture', response_code='0').aggregate(amount__sum=Coalesce(Sum('amount'), decimal.Decimal('0')))).get('amount__sum')
        reversals = dict(self.bpoint_transactions.filter(action='reversal', response_code='0').aggregate(amount__sum=Coalesce(Sum('amount'), decimal.Decimal('0')))).get('amount__sum')

        return payments - reversals

    def __calculate_bpay_payments(self):
        ''' Calcluate the amount of bpay payments made
            less the reversals for this invoice.
        '''
        payments = 0
        reversals = 0
        if self.bpay_transactions:
            payments = payments + dict(self.bpay_transactions.filter(p_instruction_code='05', type=399).aggregate(amount__sum=Coalesce(Sum('amount'), decimal.Decimal('0')))).get('amount__sum')
            reversals = dict(self.bpay_transactions.filter(p_instruction_code='25', type=699).aggregate(amount__sum=Coalesce(Sum('amount'), decimal.Decimal('0')))).get('amount__sum')

        return payments - reversals    

    def __calculate_total_refunds(self):
        ''' Calcluate the total amount of refunds
            for this invoice.
        '''
        refunds = 0
        cash_refunds = dict(self.cash_transactions.filter(type='refund').aggregate(amount__sum=Coalesce(Sum('amount'), decimal.Decimal('0')))).get('amount__sum')
        card_refunds = dict(self.bpoint_transactions.filter(action='refund', response_code='0').aggregate(amount__sum=Coalesce(Sum('amount'), decimal.Decimal('0')))).get('amount__sum')
        bpay_refunds = dict(self.bpay_transactions.filter(p_instruction_code='15', type=699).aggregate(amount__sum=Coalesce(Sum('amount'), decimal.Decimal('0')))).get('amount__sum')

        refunds = cash_refunds + card_refunds + bpay_refunds
        return refunds

    # Functions
    # =============================================
    def save(self,*args,**kwargs):
        # prevent circular import
        from ledger.payments.utils import systemid_check
        if self.pk:
            self.system = systemid_check(self.system)
        super(Invoice,self).save(*args,**kwargs)

    def make_payment(self):
        ''' Pay this invoice with the token attached to it.
        :return: BpointTransaction
        '''
        from ledger.payments.facade import bpoint_facade
        try:
            if self.token:
                card_details = self.token.split('|')
                card = TempBankCard(
                    card_details[0],
                    card_details[1]
                )
                if len(card_details) == 3:
                    card.last_digits = card_details[2]
                txn = bpoint_facade.pay_with_temptoken(
                        'payment',
                        'telephoneorder',
                        'single',
                        card,
                        self.order_number,
                        self.reference,
                        self.amount,
                        None
                    )
                if txn.approved:
                    try:
                        BpointToken.objects.get(DVToken=card_details[0])
                        self.token = ''
                        self.save()
                    except BpointToken.DoesNotExist:
                        UsedBpointToken.objects.create(DVToken=card_details[0])
                        self.token = ''
                        self.save()
                return txn
            else:
                raise ValidationError('This invoice doesn\'t have any tokens attached to it.')
        except Exception as e:
            traceback.print_exc()
            raise

class InvoiceBPAY(models.Model):
    ''' Link between unmatched bpay payments and invoices 
    '''
    invoice = models.ForeignKey(Invoice)
    bpay = models.ForeignKey('bpay.BpayTransaction')

    class Meta:
        app_label = 'payments'
        db_table = 'invoice_invoicebpay'

    def __str__(self):
        return 'Invoice No. {}: BPAY CRN {}'.format(self.invoice.reference,self.bpay.crn)


    def clean(self, *args, **kwargs):
        if (self.invoice.payment_status == 'paid' or self.invoice.payment_status == 'over_paid') and not self.pk:
            raise ValidationError('This invoice has already been paid for.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super(InvoiceBPAY,self).save(*args, **kwargs)
