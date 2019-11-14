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
from commercialoperator.components.bookings.models import BookingInvoice, ApplicationFeeInvoice


def booking_bpoint_settlement_report(_date):
    try:
        bpoint, bpay, cash = [], [], []
        bpoint.extend([x for x in BpointTransaction.objects.filter(created__date=_date,response_code=0,crn1__startswith='0557').exclude(crn1__endswith='_test')])
        bpay.extend([x for x in BpayTransaction.objects.filter(p_date__date=_date, crn__startswith='0557').exclude(crn__endswith='_test')])
        cash = CashTransaction.objects.filter(created__date=_date,invoice__reference__startswith='0557').exclude(type__in=['move_out','move_in'])

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

                try:
                    application_fee = ApplicationFeeInvoice.objects.get(invoice_reference=invoice.reference).application_fee
                except ApplicationFeeInvoice.DoesNotExist:
                    pass


                if booking:
                    b_name = u'{}'.format(booking.proposal.applicant)
                    created = timezone.localtime(b.created, pytz.timezone('Australia/Perth'))
                    settlement_date = invoice.settlement_date.strftime('%d/%m/%Y') if invoice.settlement_date else ''
                    writer.writerow([created.strftime('%d/%m/%Y %H:%M:%S'),settlement_date,booking.admission_number,b_name.encode('utf-8'),invoice.get_payment_method_display(),invoice.amount,invoice.reference])
                elif application_fee:
                    b_name = u'{}'.format(application_fee.proposal.applicant)
                    created = timezone.localtime(application_fee.created, pytz.timezone('Australia/Perth'))
                    settlement_date = invoice.settlement_date.strftime('%d/%m/%Y') if invoice.settlement_date else ''
                    writer.writerow([created.strftime('%d/%m/%Y %H:%M:%S'),settlement_date, application_fee.proposal.lodgement_number, b_name.encode('utf-8'),invoice.get_payment_method_display(),invoice.amount,invoice.reference])
                else:
                    writer.writerow([b.created.strftime('%d/%m/%Y %H:%M:%S'),b.settlement_date.strftime('%d/%m/%Y'),'','',str(b.action),b.amount,invoice.reference])
            except Invoice.DoesNotExist:
                pass

        for b in bpay:
            booking, invoice = None, None
            try:
                invoice = Invoice.objects.get(reference=b.crn)
                try:
                    booking = BookingInvoice.objects.get(invoice_reference=invoice.reference).booking
                except BookingInvoice.DoesNotExist:
                    pass

                if booking:
                    b_name = u'{}'.format(booking.proposal.applicant)
                    created = timezone.localtime(b.created, pytz.timezone('Australia/Perth'))
                    settlement_date = b.p_date.strftime('%d/%m/%Y')
                    writer.writerow([created.strftime('%d/%m/%Y %H:%M:%S'),settlement_date,booking.admission_number,b_name.encode('utf-8'),invoice.get_payment_method_display(),invoice.amount,invoice.reference])
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


#def bookings_report(_date):
#    try:
#        bpoint, cash = [], []
#        bookings = Booking.objects.filter(created__date=_date).exclude(booking_type=3)
#        admission_bookings = AdmissionsBooking.objects.filter(created__date=_date).exclude(booking_type=3)
#
#        history_bookings = BookingHistory.objects.filter(created__date=_date).exclude(booking__booking_type=3)
#
#        strIO = StringIO()
#        fieldnames = ['Date','Confirmation Number','Name','Invoice Total','Override Price','Override Reason','Override Details','Invoice','Booking Type','Created By']
#        writer = csv.writer(strIO)
#        writer.writerow(fieldnames)
#
#        types = dict(Booking.BOOKING_TYPE_CHOICES)
#        types_admissions = dict(AdmissionsBooking.BOOKING_TYPE_CHOICES)
#        for b in bookings:
#            b_name = 'No Name'
#            if b.details:
#                b_name = u'{} {}'.format(b.details.get('first_name',''),b.details.get('last_name',''))
#            created = timezone.localtime(b.created, pytz.timezone('Australia/Perth'))
#            created_by =''
#            if b.created_by is not None:
#                 created_by = b.created_by
#
#            writer.writerow([created.strftime('%d/%m/%Y %H:%M:%S'),b.confirmation_number,b_name.encode('utf-8'),b.active_invoice.amount if b.active_invoice else '',b.override_price,b.override_reason,b.override_reason_info,b.active_invoice.reference if b.active_invoice else '', types[b.booking_type] if b.booking_type in types else b.booking_type, created_by])
#
#        for b in admission_bookings:
#            b_name = 'No Name'
#            if b.customer:
#                b_name = u'{}'.format(b.customer)
#            created = timezone.localtime(b.created, pytz.timezone('Australia/Perth'))
#            created_by =''
#            if b.created_by is not None:
#                 created_by = b.created_by
#
#            writer.writerow([created.strftime('%d/%m/%Y %H:%M:%S'),b.confirmation_number,b_name.encode('utf-8'),b.active_invoice.amount if b.active_invoice else '','','','',b.active_invoice.reference if b.active_invoice else '', types_admissions[b.booking_type] if b.booking_type in types_admissions else b.booking_type, created_by])
#
#
#        #for b in history_bookings:
#        #    b_name = '{} {}'.format(b.details.get('first_name',''),b.details.get('last_name',''))
#        #    writer.writerow([b.created.strftime('%d/%m/%Y %H:%M:%S'),b.booking.confirmation_number,b_name,b.invoice.amount,b.invoice.reference,'Yes'])
#
#        strIO.flush()
#        strIO.seek(0)
#        return strIO
#    except:
#        raise
#
