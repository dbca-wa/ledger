import csv
import pytz
import datetime
from six.moves import StringIO
from wsgiref.util import FileWrapper
from django.utils import timezone
from django.core.mail import EmailMessage 
from django.conf import settings
from mooring.models import Booking, BookingInvoice, OutstandingBookingRecipient, BookingHistory
from ledger.payments.models import OracleParser,OracleParserInvoice, CashTransaction, BpointTransaction, BpayTransaction,Invoice, TrackRefund


def outstanding_bookings():
    try:
        outstanding = []
        today = datetime.date.today()
        for b in Booking.objects.filter(is_canceled=False,departure__gte=today).exclude(booking_type__in=['1','3']):
            if not b.paid:
                outstanding.append(b)


        strIO = StringIO()
        fieldnames = ['Confirmation Number','Customer','Campground','Arrival','Departure','Outstanding Amount']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)
        for o in outstanding:
            fullname = '{} {}'.format(o.details.get('first_name'),o.details.get('last_name'))
            writer.writerow([o.confirmation_number,fullname,o.campground.name,o.arrival.strftime('%d/%m/%Y'),o.departure.strftime('%d/%m/%Y'),o.outstanding])
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
        fieldnames = ['Confirmation Number', 'Name', 'Type','Amount','Oracle Code','Date','Refunded By','Reason','Invoice']
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
                    pass
                    #raise ValidationError('Couldn\'t find a booking matched to invoice reference {}'.format(e.invoice.reference))
                for line in invoice.order.lines.all():
                    for k,v in line.refund_details['cash'].items():
                        if k == str(e.id):
                            track = None
                            try:
                                track = TrackRefund.objects.get(type=1,refund_id=k)
                            except TrackRefund.DoesNotExist:
                                pass
                            name = ''
                            reason = ''
                            if track:
                                name = track.user.get_full_name() if track.user.get_full_name() else track.user.email
                                reason = track.details
                            if booking:
                                b_name = '{} {}'.format(booking.details.get('first_name',''),booking.details.get('last_name',''))
                                writer.writerow([booking.confirmation_number,b_name,'Manual',v,line.oracle_code,e.created.strftime('%d/%m/%Y'),name,reason,invoice.reference])
                            else:
                                writer.writerow(['','','Manual',v,line.oracle_code,e.created.strftime('%d/%m/%Y'),name,invoice.reference])
        for b in bpoint:
            booking, invoice = None, None
            try:
                invoice = Invoice.objects.get(reference=b.crn1)
                if invoice.system == '0019':
                    try:
                        booking = BookingInvoice.objects.get(invoice_reference=invoice.reference).booking
                    except BookingInvoice.DoesNotExist:
                        pass
                        #raise ValidationError('Couldn\'t find a booking matched to invoice reference {}'.format(e.invoice.reference))
                    for line in invoice.order.lines.all():
                        for k,v in line.refund_details['card'].items():
                            if k == str(b.id):
                                track = None
                                try:
                                    track = TrackRefund.objects.get(type=2,refund_id=k)
                                except TrackRefund.DoesNotExist:
                                    pass
                                name = ''
                                reason = ''
                                if track:
                                    name = track.user.get_full_name() if track.user.get_full_name() else track.user.email
                                    reason = track.details
                                if booking:
                                    b_name = '{} {}'.format(booking.details.get('first_name',''),booking.details.get('last_name',''))
                                    writer.writerow([booking.confirmation_number,b_name,'Card',v,line.oracle_code,b.created.strftime('%d/%m/%Y'),name,reason,invoice.reference])
                                else:
                                    writer.writerow(['','','Card',v,line.oracle_code,b.created.strftime('%d/%m/%Y'),name,invoice.reference])
            except Invoice.DoesNotExist:
                pass

        strIO.flush()
        strIO.seek(0)
        return strIO
    except:
        raise

def booking_bpoint_settlement_report(_date):
    try:
        bpoint, cash = [], []
        bpoint.extend([x for x in BpointTransaction.objects.filter(created__date=_date,response_code=0,crn1__startswith='0019').exclude(crn1__endswith='_test')])
        cash = CashTransaction.objects.filter(created__date=_date,invoice__reference__startswith='0019').exclude(type__in=['move_out','move_in'])

        strIO = StringIO()
        fieldnames = ['Payment Date','Settlement Date','Confirmation Number','Name','Type','Amount','Invoice']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)

        for b in bpoint:
            booking, invoice = None, None
            try:
                invoice = Invoice.objects.get(reference=b.crn1)
                try:
                    booking = BookingInvoice.objects.get(invoice_reference=invoice.reference).booking
                except BookingInvoice.DoesNotExist:
                    pass
                    
                if booking:
                    b_name = u'{} {}'.format(booking.details.get('first_name',''),booking.details.get('last_name',''))
                    created = timezone.localtime(b.created, pytz.timezone('Australia/Perth'))
                    writer.writerow([created.strftime('%d/%m/%Y %H:%M:%S'),b.settlement_date.strftime('%d/%m/%Y'),booking.confirmation_number,b_name.encode('utf-8'),str(b.action),b.amount,invoice.reference])
                else:
                    writer.writerow([b.created.strftime('%d/%m/%Y %H:%M:%S'),b.settlement_date.strftime('%d/%m/%Y'),'','',str(b.action),b.amount,invoice.reference])
            except Invoice.DoesNotExist:
                pass

        for b in cash:
            booking, invoice = None, None
            try:
                invoice = b.invoice 
                try:
                    booking = BookingInvoice.objects.get(invoice_reference=invoice.reference).booking
                except BookingInvoice.DoesNotExist:
                    pass
                    
                if booking:
                    b_name = u'{} {}'.format(booking.details.get('first_name',''),booking.details.get('last_name',''))
                    created = timezone.localtime(b.created, pytz.timezone('Australia/Perth'))
                    writer.writerow([created.strftime('%d/%m/%Y %H:%M:%S'),b.created.strftime('%d/%m/%Y'),booking.confirmation_number,b_name.encode('utf-8'),str(b.type),b.amount,invoice.reference])
                else:
                    writer.writerow([b.created.strftime('%d/%m/%Y %H:%M:%S'),b.created.strftime('%d/%m/%Y'),'','',str(b.type),b.amount,invoice.reference])
            except Invoice.DoesNotExist:
                pass

        strIO.flush()
        strIO.seek(0)
        return strIO
    except:
        raise

def bookings_report(_date):
    try:
        bpoint, cash = [], []
        bookings = Booking.objects.filter(created__date=_date)
        history_bookings = BookingHistory.objects.filter(created__date=_date)

        strIO = StringIO()
        fieldnames = ['Date','Confirmation Number','Name','Amount','Invoice','Booking Type']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)

        types = dict(Booking.BOOKING_TYPE_CHOICES)

        for b in bookings:
            b_name = u'{} {}'.format(b.details.get('first_name',''),b.details.get('last_name',''))
            created = timezone.localtime(b.created, pytz.timezone('Australia/Perth'))
            writer.writerow([created.strftime('%d/%m/%Y %H:%M:%S'),b.confirmation_number,b_name.encode('utf-8'),b.active_invoice.amount if b.active_invoice else '',b.active_invoice.reference if b.active_invoice else '', types[b.booking_type] if b.booking_type in types else b.booking_type])

        #for b in history_bookings:
        #    b_name = '{} {}'.format(b.details.get('first_name',''),b.details.get('last_name',''))
        #    writer.writerow([b.created.strftime('%d/%m/%Y %H:%M:%S'),b.booking.confirmation_number,b_name,b.invoice.amount,b.invoice.reference,'Yes'])
            

        strIO.flush()
        strIO.seek(0)
        return strIO
    except:
        raise
