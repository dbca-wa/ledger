import csv
import datetime
from six.moves import StringIO
from wsgiref.util import FileWrapper
from django.core.mail import EmailMessage 
from django.conf import settings
from parkstay.models import Booking, BookingInvoice, OutstandingBookingRecipient
from ledger.payments.models import OracleParser,OracleParserInvoice, CashTransaction, BpointTransaction, BpayTransaction,Invoice, TrackRefund


def outstanding_bookings():
    try:
        outstanding = []
        for b in Booking.objects.all():
            if not b.paid:
                outstanding.append(b)


        strIO = StringIO()
        fieldnames = ['Confirmation Number','Customer','Campground','Arrival','Departure','Outstanding Amount']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)
        for o in outstanding:
            writer.writerow([o.confirmation_number,o.customer.get_full_name(),o.campground.name,o.arrival.strftime('%d/%m/%Y'),o.departure.strftime('%d/%m/%Y'),o.outstanding])
        strIO.flush()
        strIO.seek(0)
        _file = strIO

        dt = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        recipients = []
        recipients = OutstandingBookingRecipient.objects.all()
        email = EmailMessage(
            'Unpaid Bookings Summary as at {}'.format(dt),
            'Unpaid Bookings as at {}'.format(dt),
            settings.DEFAULT_FROM_EMAIL,
            to=[r.email for r in recipients]if recipients else [settings.NOTIFICATION_EMAIL]
        )
        email.attach('OustandingBookings_{}.csv'.format(dt), _file.getvalue(), 'text/csv')
        email.send()
    except:
        raise

def booking_refunds(start,end):
    try:
        bpoint, cash = [], []
        bpoint.extend([x for x in BpointTransaction.objects.filter(settlement_date__gte=start, settlement_date__lte=end,action='refund',response_code=0)])
        cash.extend([x for x in CashTransaction.objects.filter(created__gte=start, created__lte=end,type='refund')])

        strIO = StringIO()
        fieldnames = ['Confirmation Number', 'Name', 'Type','Amount','Oracle Code','Date','Refunded By']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)

        # Get the required invoices
        for e in cash:
            booking, invoice = None, None
            if e.invoice.system == '0019':
                try:
                    booking = BookingInvoice.objects.get(invoice_reference=e.invoice.reference).booking
                    invoice = e.invoice
                except BookingInvoice.DoesNotExist:
                    raise ValidationError('Couldn\'t find a booking matched to invoice reference {}'.format(e.invoice.reference))
                for line in invoice.order.lines.all():
                    for k,v in line.refund_details['cash'].items():
                        if k == str(e.id) and booking.customer:
                            track = None
                            try:
                                track = TrackRefund.objects.get(type=1,refund_id=k)
                            except TrackRefund.DoesNotExist:
                                pass
                            name = ''
                            if track:
                                name = track.user.get_full_name() if track.user.get_full_name() else track.user.email
                            writer.writerow([booking.confirmation_number,booking.customer.get_full_name(),'Manual',v,line.oracle_code,e.created.strftime('%d/%m/%Y'),name])
        for b in bpoint:
            invoice = Invoice.objects.get(reference=b.crn1)
            if invoice.system == '0019':
                try:
                    booking = BookingInvoice.objects.get(invoice_reference=e.invoice.reference).booking
                except BookingInvoice.DoesNotExist:
                    raise ValidationError('Couldn\'t find a booking matched to invoice reference {}'.format(e.invoice.reference))
                for line in invoice.order.lines.all():
                    for k,v in line.refund_details['card'].items():
                        if k == str(b.id) and booking.customer:
                            track = None
                            try:
                                track = TrackRefund.objects.get(type=2,refund_id=k)
                            except TrackRefund.DoesNotExist:
                                pass
                            name = ''
                            if track:
                                name = track.user.get_full_name() if track.user.get_full_name() else track.user.email
                            writer.writerow([booking.confirmation_number,booking.customer.get_full_name(),'Card',v,line.oracle_code,b.created.strftime('%d/%m/%Y'),name])

        strIO.flush()
        strIO.seek(0)
        return strIO
    except:
        raise
