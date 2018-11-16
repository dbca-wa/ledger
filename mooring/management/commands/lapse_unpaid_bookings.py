from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from parkstay.models import Booking
from parkstay import emails
from ledger.payments.models import Invoice

from datetime import timedelta, date
from decimal import Decimal as D

import itertools

class Command(BaseCommand):
    help = 'Clear out any unpaid bookings that have lapsed'

    def handle(self, *args, **options):
        query = Booking.objects.filter(
            arrival__gt=date.today(),
            booking_type__in=(0, 1),
            created__lt=timezone.now()-timedelta(days=settings.PS_UNPAID_BOOKING_LAPSE_DAYS),
        ).prefetch_related('invoices') 

        invoice_ids = itertools.chain(*query.values_list('invoices__invoice_reference'))
        invoice_map = {i.reference: i for i in Invoice.objects.filter(reference__in=invoice_ids)}

        booking_del = []
        for booking in query:
            total = D('0.0')
            for invoice in booking.invoices.all():
                if invoice.invoice_reference in invoice_map:
                    total += invoice_map[invoice.invoice_reference].payment_amount
            if total == D('0.0'):
                print('Booking flagged for cancellation: {} {}'.format(booking.pk, booking))
                booking_del.append(booking)
        for booking in booking_del:
            emails.send_booking_lapse(booking)
            booking.is_canceled = True
            booking.campsites.all().delete()
            booking.save()
