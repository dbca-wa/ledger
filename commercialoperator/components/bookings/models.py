from __future__ import unicode_literals

import datetime
from django.db import models, transaction
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.payments.models import Invoice
from commercialoperator.components.proposals.models import Proposal
from commercialoperator.components.main.models import Park
from decimal import Decimal as D

import logging
logger = logging.getLogger(__name__)

class Payment(RevisionedMixin):
    send_invoice = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    expiry_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = 'commercialoperator'
        abstract = True

    @property
    def paid(self):
        payment_status = self.__check_payment_status()
        if payment_status == 'paid' or payment_status == 'over_paid':
            return True
        return False

    @property
    def unpaid(self):
        payment_status = self.__check_payment_status()
        if payment_status == 'unpaid':
            return True
        return False

    @property
    def amount_paid(self):
        return self.__check_payment_amount()

    def __check_payment_amount(self):
        amount = D('0.0')
        if self.active_invoice:
            return self.active_invoice.payment_amount
        return amount

    def __check_invoice_payment_status(self):
        invoices = []
        payment_amount = D('0.0')
        invoice_amount = D('0.0')
        references = self.invoices.all().values('invoice_reference')
        for r in references:
            try:
                invoices.append(Invoice.objects.get(reference=r.get("invoice_reference")))
            except Invoice.DoesNotExist:
                pass
        for i in invoices:
            if not i.voided:
                payment_amount += i.payment_amount
                invoice_amount += i.amount

        if invoice_amount == payment_amount:
            return 'paid'
        if payment_amount > invoice_amount:
            return 'over_paid'
        return "unpaid"

    def __check_payment_status(self):
        invoices = []
        amount = D('0.0')
        references = self.invoices.all().values('invoice_reference')
        for r in references:
            try:
                invoices.append(Invoice.objects.get(reference=r.get("invoice_reference")))
            except Invoice.DoesNotExist:
                pass
        for i in invoices:
            if not i.voided:
                amount += i.payment_amount

        if amount == 0:
            return 'unpaid'
        elif self.cost_total < amount:
            return 'over_paid'
        elif self.cost_total > amount:
            return 'partially_paid'
        return "paid"


class Booking(Payment):
    BOOKING_TYPE_INTERNET = 0
    BOOKING_TYPE_CHOICES = (
        (BOOKING_TYPE_INTERNET, 'Internet booking'),
        (1, 'Reception booking'),
        (2, 'Black booking'),
        (3, 'Temporary reservation'),
#        (4, 'Cancelled Booking'),
#        (5, 'Changed Booking')
    )

    proposal = models.ForeignKey(Proposal, on_delete=models.PROTECT, blank=True, null=True, related_name='bookings')
    booking_type = models.SmallIntegerField(choices=BOOKING_TYPE_CHOICES, default=0)
    admission_number = models.CharField(max_length=9, blank=True, default='')
    created_by = models.ForeignKey(EmailUser,on_delete=models.PROTECT, blank=True, null=True,related_name='created_by_booking')

    def __str__(self):
        return 'Application {} : Invoice {}'.format(self.proposal, self.invoices.last())

    class Meta:
        app_label = 'commercialoperator'

    @property
    def next_id(self):
        ids = map(int,[i.split('AD')[1] for i in Booking.objects.all().values_list('admission_number', flat=True) if i])
        return max(ids) + 1 if ids else 1

    def save(self, *args, **kwargs):
        super(Booking, self).save(*args,**kwargs)
        if self.admission_number == '':
            self.admission_number = 'AD{0:06d}'.format(self.next_id)
            self.save()

    @property
    def booking_number(self):
        return 'COLS-{0:06d}'.format(self.id)

    @property
    def num_visitors(self):
        if self.park_bookings:
            for park_booking in park_bookings:
                num_visitors += park_booking.num_visitors
            return num_visitors
        return 0

    @property
    def visitors(self):
        if self.park_bookings:
            for park_booking in park_bookings:
                no_adults += park_booking.no_adults
                no_children += park_booking.no_children
                no_free_of_charge += park_booking.no_free_of_charge
            return {
                "adults" : no_adultis,
                "children" : no_children,
                "free_of_charge" : no_free_of_charge
            }
        return {
            "adults" : 0,
            "children" : 0,
            "free_of_charge" : 0
        }

    @property
    def park_id_list(self):
        #return list(set([x['campsite'] for x in self.campsites.all().values('campsite')]))
        return self.park_bookings.all().values('park_id')

    @property
    def park_name_list(self):
        #return list(set(self.campsites.values_list('campsite__name', flat=True)))
        return self.park_bookings.all().values('park__name')


class ParkBooking(RevisionedMixin):
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, blank=True, null=True, related_name='park_bookings')
    park = models.ForeignKey(Park, related_name='bookings')
    arrival = models.DateField()
    no_adults = models.SmallIntegerField(default=0)
    no_children = models.SmallIntegerField(default=0)
    no_free_of_charge = models.SmallIntegerField(default=0)
    cost = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')

    def __str__(self):
        return 'Park {} : Arrival {} (Adults {}, Children {}, Free {})'.format(self.park.name, self.arrival, self.no_adults, self.no_children, self.no_free_of_charge)

    class Meta:
        app_label = 'commercialoperator'

    @property
    def num_visitors(self):
        return self.no_adults + self.no_children + self.no_free_of_charge

    @property
    def visitors(self):
        return {
            "adults" : self.no_adults,
            "children" : self.no_cildrenn,
            "free_of_charge" : self.no_free_of_charge
        }


class BookingInvoice(RevisionedMixin):
    booking = models.ForeignKey(Booking, related_name='invoices')
    invoice_reference = models.CharField(max_length=50, null=True, blank=True, default='')

    def __str__(self):
        return 'Booking {} : Invoice #{}'.format(self.id,self.invoice_reference)

    class Meta:
        app_label = 'commercialoperator'

    @property
    def active(self):
        try:
            invoice = Invoice.objects.get(reference=self.invoice_reference)
            return False if invoice.voided else True
        except Invoice.DoesNotExist:
            pass
        return False

class ApplicationFee(Payment):
    PAYMENT_TYPE_INTERNET = 0
    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE_INTERNET, 'Internet booking'),
        (1, 'Reception booking'),
        (2, 'Black booking'),
        (3, 'Temporary reservation'),
#        (4, 'Cancelled Booking'),
#        (5, 'Changed Booking')
    )

    proposal = models.ForeignKey(Proposal, on_delete=models.PROTECT, blank=True, null=True, related_name='application_fees')
    payment_type = models.SmallIntegerField(choices=PAYMENT_TYPE_CHOICES, default=0)
    cost = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    created_by = models.ForeignKey(EmailUser,on_delete=models.PROTECT, blank=True, null=True,related_name='created_by_application_fee')

    def __str__(self):
        return 'Application {} : Invoice {}'.format(self.proposal, self.application_fee_invoices.last())

    class Meta:
        app_label = 'commercialoperator'

class ApplicationFeeInvoice(RevisionedMixin):
    application_fee = models.ForeignKey(ApplicationFee, related_name='application_fee_invoices')
    invoice_reference = models.CharField(max_length=50, null=True, blank=True, default='')

    def __str__(self):
        return 'Application Fee {} : Invoice #{}'.format(self.id,self.invoice_reference)

    class Meta:
        app_label = 'commercialoperator'

    @property
    def active(self):
        try:
            invoice = Invoice.objects.get(reference=self.invoice_reference)
            return False if invoice.voided else True
        except Invoice.DoesNotExist:
            pass
        return False


#import reversion
#reversion.register(Booking, follow=['invoices', 'park_bookings'])
#reversion.register(ParkBooking)
#reversion.register(BookingInvoice)
#reversion.register(ApplicationFee, follow=['application_fee_invoices'])
#reversion.register(ApplicationFeeInvoice)


