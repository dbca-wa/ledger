from __future__ import unicode_literals

from datetime import datetime, timedelta
from django.db import models, transaction
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from ledger.accounts.models import EmailUser, RevisionedMixin
from ledger.payments.models import Invoice
from commercialoperator.components.proposals.models import Proposal
from commercialoperator.components.main.models import Park
from decimal import Decimal as D
from ledger.checkout.utils import calculate_excl_gst

import logging
logger = logging.getLogger(__name__)

class Payment(RevisionedMixin):

    send_invoice = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now())
    expiry_time = models.DateTimeField(default=timezone.now() + timedelta(minutes=30), blank=True, null=True)

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
    BOOKING_TYPE_RECEPTION = 1
    BOOKING_TYPE_BLACK = 2
    BOOKING_TYPE_TEMPORARY = 3
    BOOKING_TYPE_MONTHLY_INVOICING = 4
    BOOKING_TYPE_CHOICES = (
        (BOOKING_TYPE_INTERNET, 'Internet booking'),
        (BOOKING_TYPE_RECEPTION, 'Reception booking'),
        (BOOKING_TYPE_BLACK, 'Black booking'),
        (BOOKING_TYPE_TEMPORARY, 'Temporary reservation'),
        (BOOKING_TYPE_MONTHLY_INVOICING, 'Monthly invoicing'),
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

#    def set_admission_number(self):
#        """ Need to set admission_number after Credit Card Payment is successfully completed i.e. after BookingSuccessView.get() is executed.
#            Prior to this, the Booking object is temporary.
#        """
#        if self.admission_number == '':
#            self.admission_number = 'AD{0:06d}'.format(self.next_id)
#            self.save()

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
                "adults" : no_adults,
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

    @property
    def as_line_items(self):
        """ returns a dict line item equiv of the Booking Object for ledger checkout """

        lines = []
        for park_booking in self.park_bookings.all():
            lines += park_booking.as_line_items
        return lines

    @property
    def invoice(self):
        return self.invoices.last().invoice

    @property
    def deferred_payment_date(self):
        return self.invoices.last().deferred_payment_date

class ParkBooking(RevisionedMixin):
    created = models.DateTimeField(default=timezone.now())
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
            "children" : self.no_children,
            "free_of_charge" : self.no_free_of_charge
        }

    @property
    def as_line_items(self):
        """ returns a dict line item equiv of the ParkBooking Object for ledger checkout (aggregated via Booking object)"""
        def add_line_item(age_group, price, no_persons):
            if no_persons > 0:
                return {
                    'ledger_description': 'Booking Date {}: {} - {} - {}'.format(self.created.date(), self.park.name, self.arrival, age_group),
                    'oracle_code': self.park.oracle_code,
                    'price_incl_tax':  D(price),
                    'price_excl_tax':  D(price) if self.park.is_gst_exempt else calculate_excl_gst(D(price)),
                    'quantity': no_persons,
                }
            return None

        lines = []
        if self.no_adults > 0:
            lines.append(add_line_item('Adult', price=self.park.adult_price, no_persons=self.no_adults))

        if self.no_children > 0:
            lines.append(add_line_item('Child', price=self.park.child_price, no_persons=self.no_children))

        if self.no_free_of_charge > 0:
            lines.append(add_line_item('Free', price=0.0, no_persons=self.no_free_of_charge))

        return lines


class BookingInvoice(RevisionedMixin):
    PAYMENT_METHOD_CC = 0
    PAYMENT_METHOD_BPAY = 1
    PAYMENT_METHOD_MONTHLY_INVOICING = 2
    PAYMENT_METHOD_OTHER = 3
    PAYMENT_METHOD_CHOICES = (
        (PAYMENT_METHOD_CC, 'Credit Card'),
        (PAYMENT_METHOD_BPAY, 'BPAY'),
        (PAYMENT_METHOD_MONTHLY_INVOICING, 'Monthly Invoicing'),
        (PAYMENT_METHOD_OTHER, 'Other (Cash/Cheque)'),
    )

    booking = models.ForeignKey(Booking, related_name='invoices')
    invoice_reference = models.CharField(max_length=50, null=True, blank=True, default='')
    payment_method = models.SmallIntegerField(choices=PAYMENT_METHOD_CHOICES, default=0) # duplicating from ledger Invoice model to allow easier filtering on payment dashboard
    deferred_payment_date = models.DateField(blank=True, null=True)
    payment_due_notification_sent = models.BooleanField(default=False)

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

    @property
    def invoice(self):
        try:
            invoice = Invoice.objects.get(reference=self.invoice_reference)
            return invoice
        except Invoice.DoesNotExist:
            pass
        return False

    @property
    def overdue(self):
        if self.invoice and self.invoice.settlement_date and (self.invoice.payment_status == 'unpaid' or self.invoice.payment_status == 'partially_paid') and self.invoice.settlement_date<timezone.now().date():
            return True
        return False


class ApplicationFee(Payment):
    PAYMENT_TYPE_INTERNET = 0
    PAYMENT_TYPE_RECEPTION = 1
    PAYMENT_TYPE_BLACK = 2
    PAYMENT_TYPE_TEMPORARY = 3
    PAYMENT_TYPE_CHOICES = (
        (PAYMENT_TYPE_INTERNET, 'Internet booking'),
        (PAYMENT_TYPE_RECEPTION, 'Reception booking'),
        (PAYMENT_TYPE_BLACK, 'Black booking'),
        (PAYMENT_TYPE_TEMPORARY, 'Temporary reservation'),
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


import reversion
reversion.register(Booking, follow=['invoices', 'park_bookings'])
reversion.register(ParkBooking)
reversion.register(BookingInvoice)
reversion.register(ApplicationFee, follow=['application_fee_invoices'])
reversion.register(ApplicationFeeInvoice)


