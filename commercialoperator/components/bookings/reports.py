import csv
import pytz
import datetime
from six.moves import StringIO
from wsgiref.util import FileWrapper
from django.utils import timezone
from django.core.mail import EmailMessage
from django.conf import settings
#from mooring.models import Booking, BookingInvoice, OutstandingBookingRecipient, BookingHistory, AdmissionsBooking, AdmissionsBookingInvoice
from ledger.payments.models import OracleParser,OracleParserInvoice, CashTransaction, BpointTransaction, BpayTransaction,Invoice, TrackRefund

def bookings_report(_date):
    try:
        bpoint, cash = [], []
        bookings = Booking.objects.filter(created__date=_date).exclude(booking_type=3)
        admission_bookings = AdmissionsBooking.objects.filter(created__date=_date).exclude(booking_type=3)

        history_bookings = BookingHistory.objects.filter(created__date=_date).exclude(booking__booking_type=3)

        strIO = StringIO()
        fieldnames = ['Date','Confirmation Number','Name','Invoice Total','Override Price','Override Reason','Override Details','Invoice','Booking Type','Created By']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)

        types = dict(Booking.BOOKING_TYPE_CHOICES)
        types_admissions = dict(AdmissionsBooking.BOOKING_TYPE_CHOICES)
        for b in bookings:
            b_name = 'No Name'
            if b.details:
                b_name = u'{} {}'.format(b.details.get('first_name',''),b.details.get('last_name',''))
            created = timezone.localtime(b.created, pytz.timezone('Australia/Perth'))
            created_by =''
            if b.created_by is not None:
                 created_by = b.created_by

            writer.writerow([created.strftime('%d/%m/%Y %H:%M:%S'),b.confirmation_number,b_name.encode('utf-8'),b.active_invoice.amount if b.active_invoice else '',b.override_price,b.override_reason,b.override_reason_info,b.active_invoice.reference if b.active_invoice else '', types[b.booking_type] if b.booking_type in types else b.booking_type, created_by])

        for b in admission_bookings:
            b_name = 'No Name'
            if b.customer:
                b_name = u'{}'.format(b.customer)
            created = timezone.localtime(b.created, pytz.timezone('Australia/Perth'))
            created_by =''
            if b.created_by is not None:
                 created_by = b.created_by

            writer.writerow([created.strftime('%d/%m/%Y %H:%M:%S'),b.confirmation_number,b_name.encode('utf-8'),b.active_invoice.amount if b.active_invoice else '','','','',b.active_invoice.reference if b.active_invoice else '', types_admissions[b.booking_type] if b.booking_type in types_admissions else b.booking_type, created_by])


        #for b in history_bookings:
        #    b_name = '{} {}'.format(b.details.get('first_name',''),b.details.get('last_name',''))
        #    writer.writerow([b.created.strftime('%d/%m/%Y %H:%M:%S'),b.booking.confirmation_number,b_name,b.invoice.amount,b.invoice.reference,'Yes'])

        strIO.flush()
        strIO.seek(0)
        return strIO
    except:
        raise

