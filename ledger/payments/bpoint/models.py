from __future__ import unicode_literals
import datetime
from decimal import Decimal as D
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from ledger.payments.bpoint import settings as bpoint_settings
from django.utils.encoding import python_2_unicode_compatible
from oscar.apps.order.models import Order
from ledger.accounts.models import EmailUser

class BpointTransaction(models.Model):
    ACTION_TYPES = (
        ('payment','payment'),
        ('refund','refund'),
        ('unmatched_refund','unmatched_refund'),
        ('reversal','reversal'),
        ('preauth', 'preauth'),
        ('capture','capture')
    )
    CARD_TYPES = (
        ('AX','American Express'),
        ('DC','Diners Club'),
        ('JC','JCB Card'),
        ('MC','MasterCard'),
        ('VC','Visa')
    )
    SUB_TYPES = (
        ('single','single'),
        ('recurring','recurring')
    )
    TRANSACTION_TYPES = (
        ('callcentre','callcentre'),
        ('cardpresent','cardpresent'),
        ('ecommerce','ecommerce'),
        ('internet', 'internet'),
        ('ivr','ivr'),
        ('mailorder','mailorder'),
        ('telephoneorder','telephoneorder')
    )
    created = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    amount = models.DecimalField(decimal_places=2,max_digits=12)
    amount_original = models.DecimalField(decimal_places=2,max_digits=12)
    amount_surcharge = models.DecimalField(default=0,decimal_places=2,max_digits=12)
    cardtype = models.CharField(max_length=2, choices=CARD_TYPES, blank=True, null=True)
    crn1 = models.CharField(max_length=50, help_text='Reference for the order that the transaction was made for')
    response_code = models.CharField(max_length=50)
    response_txt = models.CharField(max_length=128)
    receipt_number = models.CharField(max_length=50)
    processed = models.DateTimeField()
    settlement_date = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    # store the txn number from Bpoint
    txn_number = models.CharField(unique=True, max_length=128, help_text='Transaction number used by BPOINT to identify a transaction')
    original_txn = models.ForeignKey('self', to_field='txn_number', blank=True, null=True, help_text='Transaction number stored \
                                           if current transaction depends on a previous transaction \
                                           in the case where the action is a refund, reversal or capture')
    dvtoken = models.CharField(max_length=128,null=True,blank=True,help_text='Stored card dv token')
    last_digits = models.CharField(max_length=4,blank=True,null=True,help_text='Last four digits of card used during checkout')
    
    class Meta:
        ordering = ('-created',)
    
    def __unicode__(self):
        return self.txn_number
    
    @property
    def approved(self):
        return self.response_code == "0"
    
    @property
    def order(self):
        from ledger.payments.models import Invoice
        return Order.objects.get(number=Invoice.objects.get(reference=self.crn1).order_number)

    @property
    def refundable_amount(self):
        amount = D('0.0')
        if self.action== 'payment' or self.action== 'capture':
            refunds  = BpointTransaction.objects.filter(Q(action='refund') | Q(action='unnmatched_refund'),original_txn=self.txn_number)
            for r in refunds:
                amount += r.amount
        return self.amount - amount

    # Methods
    # ==============================
    def refund(self,amount,matched=True):
        from ledger.payments.bpoint.facade import bpoint_facade 
        try:
            txn = None
            if self.action != 'payment' or self.action != 'capture':
                raise ValidationError('The transaction has to be either a payment or capture in order to make a refund.')

            if self.approved:
                txn = bpoint_facade.pay_with_temptoken(
                            'refund' if matched else 'unmatched_refund',
                            'telephoneorder',
                            'single',
                            card,
                            self.order_number,
                            self.reference,
                            amount,
                            self.txn_number 
                        )
                if txn.approved:
                    try:
                        BpointToken.objects.get(DVToken=txn.dvtoken)
                    except BpointToken.DoesNotExist:
                        UsedBpointToken.objects.create(DVToken=txn.dvtoken)
            else:
                raise ValidationError('A refund cannot be made to an unnapproved tranascation.')
            return txn 
        except:
            raise

class TempBankCard(object):
    def __init__(self,card_number,expiry_date,ccv=None):
        self.number=card_number
        self.expiry_date=datetime.datetime.strptime(expiry_date, '%m%y').date()
        self.ccv=ccv

class BpointToken(models.Model):
    CARD_TYPES = (
        ('AX','American Express'),
        ('DC','Diners Club'),
        ('JC','JCB Card'),
        ('MC','MasterCard'),
        ('VC','Visa')
    )
    user = models.ForeignKey(EmailUser, related_name='stored_cards')
    DVToken = models.CharField(max_length=128)
    masked_card = models.CharField(max_length=50)
    expiry_date = models.DateField()
    card_type = models.CharField(max_length=2, choices=CARD_TYPES, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'masked_card','expiry_date','card_type')

    @property
    def last_digits(self):
        return self.masked_card[-4:]

    @property
    def bankcard(self):
        return TempBankCard(
            self.DVToken,
            self.expiry_date.strftime("%m%y")
        )

    def delete(self):
        UsedBpointToken.objects.create(DVToken=self.DVToken)
        super(BpointToken,self).delete()

class UsedBpointToken(models.Model):
    added = models.DateTimeField(auto_now_add=True)
    DVToken = models.CharField(max_length=128)
