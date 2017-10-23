from __future__ import unicode_literals
import decimal
from django.db import models
from django.core.exceptions import ValidationError
from ledger.payments.bpoint import settings as bpoint_settings
from django.utils.encoding import python_2_unicode_compatible
from ledger.payments.invoice.models import Invoice

DISTRICT_PERTH_HILLS = 'PHS'
DISTRICT_SWAN_COASTAL = 'SWC'
DISTRICT_BLACKWOOD = 'BWD'
DISTRICT_WELLINGTON = 'WTN'
DISTRICT_DONNELLY = 'DON'
DISTRICT_FRANKLAND = 'FRK'
DISTRICT_ALBANY = 'ALB'
DISTRICT_ESPERANCE = 'ESP'
DISTRICT_EAST_KIMBERLEY = 'EKM'
DISTRICT_WEST_KIMBERLEY = 'WKM'
DISTRICT_EXMOUTH = 'EXM'
DISTRICT_PILBARA = 'PIL'
DISTRICT_KALGOORLIE = 'KAL'
DISTRICT_GERALDTON = 'GER'
DISTRICT_MOORA = 'MOR'
DISTRICT_SHARK_BAY = 'SHB'
DISTRICT_GREAT_SOUTHERN = 'GSN'
DISTRICT_CENTRAL_WHEATBELT = 'CWB'
DISTRICT_SOUTHERN_WHEATBELT = 'SWB'

DISTRICT_CHOICES = (
    (DISTRICT_PERTH_HILLS, "Perth Hills"),
    (DISTRICT_SWAN_COASTAL, "Swan Coastal"),
    (DISTRICT_BLACKWOOD, "Blackwood"),
    (DISTRICT_WELLINGTON, "Wellington"),
    (DISTRICT_DONNELLY, "Donnelly"),
    (DISTRICT_FRANKLAND, "Frankland"),
    (DISTRICT_ALBANY, "Albany"),
    (DISTRICT_ESPERANCE, "Esperance"),
    (DISTRICT_EAST_KIMBERLEY, "East Kimberley"),
    (DISTRICT_WEST_KIMBERLEY, "West Kimberley"),
    (DISTRICT_EXMOUTH, "Exmouth"),
    (DISTRICT_PILBARA, "Pilbara"),
    (DISTRICT_KALGOORLIE, "Kalgoorlie"),
    (DISTRICT_GERALDTON, "Geraldton"),
    (DISTRICT_MOORA, "Moora"),
    (DISTRICT_SHARK_BAY, "Shark Bay"),
    (DISTRICT_GREAT_SOUTHERN, "Great Southern"),
    (DISTRICT_CENTRAL_WHEATBELT, "Central Wheatbelt"),
    (DISTRICT_SOUTHERN_WHEATBELT, "Southern Wheatbelt")
)

REGION_KIMBERLEY = 'kimberley'
REGION_PILBARA = 'pilbara'
REGION_MIDWEST = 'midwest'
REGION_GOLDFIELDS = 'goldfields'
REGION_SWAN = 'swan'
REGION_WHEATBELT = 'wheatbelt'
REGION_SOUTH_WEST = 'southwest'
REGION_WARREN = 'warren'
REGION_SOUTH_COAST = 'southcoast'

REGION_CHOICES = (
    (REGION_KIMBERLEY,'Kimberley'),
    (REGION_PILBARA,'Pilbara'),
    (REGION_MIDWEST,'Midwest'),
    (REGION_GOLDFIELDS,'Goldfields'),
    (REGION_SWAN,'Swan'),
    (REGION_WHEATBELT,'Wheatbelt'),
    (REGION_SOUTH_WEST,'South West'),
    (REGION_WARREN,'Warren'),
    (REGION_SOUTH_COAST,'South Coast')
)

class Region(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'payments_region'

class District(models.Model):
    name = models.CharField(choices=DISTRICT_CHOICES,max_length=3,unique=True)
    region = models.ForeignKey(Region,related_name='districts')

    class Meta:
        db_table = 'payments_district'

class CashTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('payment','payment'),
        ('refund','refund'),
        ('reversal','reversal'),
        ('move_in','Move Funds In'),
        ('move_out','Move Funds out')
    )
    SOURCE_TYPES = (
        ('cash','cash'),
        ('cheque', 'cheque'),
        ('eftpos','eftpos'),
        ('money_order','money_order')
    )
    invoice = models.ForeignKey(Invoice, related_name='cash_transactions', to_field='reference')
    amount = models.DecimalField(decimal_places=2,max_digits=12)
    created = models.DateTimeField(auto_now_add=True)
    original_txn = models.ForeignKey('self', null=True, blank=True)
    type = models.CharField(choices=TRANSACTION_TYPES, max_length=8)
    source = models.CharField(choices=SOURCE_TYPES, max_length=11)
    region = models.CharField(choices=REGION_CHOICES, max_length=50, blank=True,null=True)
    district = models.CharField(choices=DISTRICT_CHOICES,max_length=3, null=True, blank=True)
    external = models.BooleanField(default=False)
    receipt = models.CharField(max_length=128,null=True,blank=True)
    details = models.TextField(null=True, blank=True)
    movement_reference = models.CharField(max_length=50,null=True,blank=True)
    class Meta:
        db_table = 'payments_cashtransaction'

    def save(self, *args, **kwargs):
        # Validations
        self.full_clean()

        super(CashTransaction, self).save(*args, **kwargs)

    def clean(self, *args, **kwargs):
        if not self.receipt and self.external:
            raise ValidationError("A receipt number is required for an external payment.ie receipt")
        if not (self.region or self.district) and self.external:
            raise ValidationError("A region or district is required for an external payment.ie region/district")
        if self.type in ['reversal','refund'] and self.invoice.payment_status == 'unpaid':
            raise ValidationError("A {} cannot be made for an unpaid invoice.".format(self.type))
        if self.type == 'refund' and (self.invoice.payment_amount < decimal.Decimal(self.amount)):
            raise ValidationError("A refund greater than the amount paid for the invoice cannot be made.")
        if self.type  in ['move_out','move_in'] and self.source != 'cash':
            raise ValidationError('A movement of funds must always have the source as cash')
        if self.type in ['move_in','move_out'] and not self.movement_reference:
            if self.type == 'move_out':
                raise ValidationError('A reference number is required to show where the funds are moving to.')
            elif self.type == 'move_in':
                raise ValidationError('A reference number is required to show where the funds are coming from.')
        if self.pk is None:
            if self.invoice.voided and self.type not in ['move_out','refund']:
                raise ValidationError('You cannot make a payment to voided invoice')
            if self.invoice.payment_status == 'paid' and self.type == 'payment':
                raise ValidationError('This invoice has already been paid for.')
            if (decimal.Decimal(self.amount) > self.invoice.balance) and self.type == 'payment':
                raise ValidationError('The amount to be charged is more than the amount payable for this invoice.')
            if (decimal.Decimal(self.amount) > self.invoice.refundable_amount) and self.type == 'refund':
                raise ValidationError('The amount to be refunded is more than the amount refundable for this invoice.')
        else:
            orig = CashTransaction.objects.get(pk=self.pk)
            if orig.amount != self.amount:
                raise ValidationError('The amount cannot be changed after the transaction has been inserted.')
            if orig.type != self.type:
                raise ValidationError('The transaction type cannot be changed after the transaction has been inserted.')
            if (not orig.external and not self.external) and (self.region or self.district):
                raise ValidationError('You need to make this transaction external before adding region/district.')
            if orig.external and not self.external:
                self.district = None
                self.region = None
                self.receipt = None

    @property
    def payment_allocated(self):
        allocated = decimal.Decimal('0.0')
        invoice = self.invoice
        if invoice.order:
            lines = invoice.order.lines.all()
            for line in lines:
                for k,v in line.payment_details.items():
                    if k == 'cash':
                        for i,a in v.items():
                            if i == str(self.id):
                                allocated += decimal.Decimal(a)
        return allocated

    @property
    def refund_allocated(self):
        allocated = decimal.Decimal('0.0')
        invoice = self.invoice
        if invoice.order:
            lines = invoice.order.lines.all()
            for line in lines:
                for k,v in line.refund_details.items():
                    if k == 'cash':
                        for i,a in v.items():
                            if i == str(self.id):
                                allocated += decimal.Decimal(a)
        return allocated

    @property
    def deduction_allocated(self):
        allocated = decimal.Decimal('0.0')
        invoice = self.invoice
        if invoice.order:
            lines = invoice.order.lines.all()
            for line in lines:
                for k,v in line.deduction_details.items():
                    if k == 'cash':
                        for i,a in v.items():
                            if i == str(self.id):
                                allocated += decimal.Decimal(a)
        return allocated
