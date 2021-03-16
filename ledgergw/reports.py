import csv
import pytz
import datetime
from six.moves import StringIO
from wsgiref.util import FileWrapper
from django.utils import timezone
from django.core.mail import EmailMessage 
from django.conf import settings
from mooring.models import Booking, BookingInvoice, OutstandingBookingRecipient, BookingHistory, AdmissionsBooking, AdmissionsBookingInvoice
from ledger.payments.models import OracleParser,OracleParserInvoice, CashTransaction, BpointTransaction, BpayTransaction,Invoice, TrackRefund
from mooring import models
from datetime import timedelta
from django.db.models import Q, Min

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
def annual_admissions_booking_report(aadata):
    try:
        bookings = []
        today = datetime.date.today()
        strIO = StringIO()
        fieldnames = ['ID','First Name','Last Name','Email','Mobile','Phone','Vessel Name','Vessel Rego','Vessel Length','Sticker No','Year','Status','Booking Period','Postal Address 1','Postal Address 2','Suburb','Post Code','State','Country' ]
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)
        for o in aadata:
            email = ''
            country = ''
            postal_address_line_1 = ''
            postal_address_line_2 = ''
            post_code = ''
            state = ''
            vessel_length = ''
            vessel_name = ''
            vessel_rego = ''
            phone = ''
            mobile = ''
            sticker_no = ''
            suburb = ''
            first_name = ''
            last_name  = ''
            email = ''
            if o['sticker_no']:
                 sticker_no = o['sticker_no']
            if o['details']:
                phone = o['details']['phone']
                mobile = o['details']['mobile']
                email = o['details']['email']
                vessel_length = o['details']['vessel_length']
                vessel_name = o['details']['vessel_name']
                vessel_rego = o['details']['vessel_rego']
                country = o['details']['country']
                postal_address_line_1 = o['details']['postal_address_line_1']
                postal_address_line_2 = o['details']['postal_address_line_2']
                state = o['details']['state']
                vessel_length = o['details']['vessel_length']
                if 'post_code' in o['details']:
                   post_code = o['details']['post_code']         
                if 'suburb' in o['details']:
                   suburb = o['details']['suburb'] 
                if 'first_name' in  o['details']:
                   first_name = o['details']['first_name']
                else:
                   first_name = o['customer']['first_name']

                if 'last_name' in o['details']:
                   last_name = o['details']['last_name']
                else:
                   last_name = o['customer']['last_name']
                        
            writer.writerow(['AA'+str(o['id']),first_name,last_name,email,mobile,phone,vessel_name,vessel_rego,vessel_length,sticker_no,o['year'],o['status'],o['annual_booking_period_group_name'],postal_address_line_1,postal_address_line_2,suburb,post_code,state,country])

        strIO.flush()
        strIO.seek(0)
        return strIO

    except:
        raise


def mooring_booking_created(start,end):
    try:

        strIO = StringIO()
        fieldnames = ['Booking ID', 'Arrival', 'Departure','Booking Type','Cost Total','Cancelled','Created','Customer ID','Phone','Mobile','First Name','Last Name','Admission Booking ID']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)
        bookings = models.Booking.objects.filter(Q(created__gte=start, created__lte=end) & Q(Q(booking_type=1) | Q(booking_type=4) | Q(booking_type=5)))
        for b in bookings:
            admission_id = ''
            customer_id = ''
            first_name = ''
            last_name = ''
            created_nice = ''
            phone = ''
            mobile ='' 
            if b.admission_payment:
                admission_id = b.admission_payment.id
            if b.customer:
                customer_id = b.customer.id
            if b.details:
                if 'first_name' in b.details:
                   first_name = b.details['first_name']
                if 'last_name' in b.details:
                   last_name = b.details['last_name']
                if 'phone' in b.details:
                    phone = b.details['phone']
                if 'mobile' in b.details:
                    mobile = b.details['mobile']

                created = b.created + timedelta(hours=8)
                created_nice = created.strftime('%d/%m/%Y %H:%M')
            writer.writerow([b.id,b.arrival,b.departure,b.get_booking_type_display(),b.cost_total,b.is_canceled,created_nice,customer_id,phone,mobile,first_name,last_name,admission_id])

        strIO.flush()
        strIO.seek(0)
        return strIO
    except:
        raise


def admission_booking_created(start,end):
    try:

        strIO = StringIO()
        fieldnames = ['Admission Booking ID','Booking Type','Cost Total','Created','Customer ID','Mobile','First Name','Last Name']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)
        bookings = models.AdmissionsBooking.objects.filter(Q(created__gte=start, created__lte=end) & Q(Q(booking_type=1) | Q(booking_type=4) | Q(booking_type=5)))
        for b in bookings:
            admission_id = ''
            customer_id = ''
            first_name = ''
            last_name = ''
            created_nice = ''
            if b.customer:
                customer_id = b.customer.id
                first_name = b.customer.first_name
                last_name = b.customer.last_name
                created = b.created + timedelta(hours=8)
                created_nice = created.strftime('%d/%m/%Y %H:%M')

            writer.writerow([b.id,b.get_booking_type_display(),b.totalCost,created_nice,customer_id,b.mobile,first_name,last_name])

        strIO.flush()
        strIO.seek(0)
        return strIO
    except:
        raise

def mooring_booking_departure(start,end):
    try:

        strIO = StringIO()
        fieldnames = ['Booking ID', 'Arrival', 'Departure','Booking Type','Cost Total','Cancelled','Created','Customer ID','Phone','First Name','Last Name','Admission Booking ID']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)
        bookings = models.Booking.objects.filter(Q(departure__gte=start, departure__lte=end) & Q(Q(booking_type=1) | Q(booking_type=4) | Q(booking_type=5)))
        for b in bookings:
            admission_id = ''
            customer_id = ''
            first_name = ''
            last_name = ''
            created_nice = ''
            if b.admission_payment:
                admission_id = b.admission_payment.id
            if b.customer:
                customer_id = b.customer.id
            if b.details:
                if 'first_name' in b.details:
                   first_name = b.details['first_name']
                if 'last_name' in b.details:
                   last_name = b.details['last_name']
                created = b.created + timedelta(hours=8)
                created_nice = created.strftime('%d/%m/%Y %H:%M')
            writer.writerow([b.id,b.arrival,b.departure,b.get_booking_type_display(),b.cost_total,b.is_canceled,created_nice,customer_id,first_name,last_name,admission_id])

        strIO.flush()
        strIO.seek(0)
        return strIO
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
            if e.invoice.system == '0516':
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
            admission_booking = None
            try:
                invoice = Invoice.objects.get(reference=b.crn1)
                if invoice.system == '0516':
                    try:
                        if BookingInvoice.objects.filter(invoice_reference=invoice.reference).count() > 0:
                            booking_row = BookingInvoice.objects.filter(invoice_reference=invoice.reference)[0]
                            if booking_row.booking: 
                                 booking = booking_row.booking
                        else:
                            if AdmissionsBookingInvoice.objects.filter(invoice_reference=invoice.reference).count() > 0:
                                 booking_row = AdmissionsBookingInvoice.objects.filter(invoice_reference=invoice.reference)[0]
                                 if booking_row.admissions_booking:
                                     admission_booking = booking_row.admissions_booking
                              
                    except BookingInvoice.DoesNotExist:
                        pass
                        #raise ValidationError('Couldn\'t find a booking matched to invoice reference {}'.format(e.invoice.reference))
                    for line in invoice.order.lines.all():
                        for k,v in line.payment_details['order'].items():
                            #if k == str(b.id): # removed as not valid under the allocation scenario
                            track = None
                            try:
                                track = TrackRefund.objects.get(type=2,refund_id=b.id)
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
                            elif admission_booking:
                                b_name = '{}' .format(admission_booking.customer)
                                writer.writerow([admission_booking.confirmation_number,b_name,'Card',v,line.oracle_code,b.created.strftime('%d/%m/%Y'),name,reason,invoice.reference])
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
        bpoint.extend([x for x in BpointTransaction.objects.filter(settlement_date=_date,response_code=0,crn1__startswith='0516').exclude(crn1__endswith='_test')])
        cash = CashTransaction.objects.filter(created__date=_date,invoice__reference__startswith='0516').exclude(type__in=['move_out','move_in'])

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
        bookings = Booking.objects.filter(created__date=_date).exclude(booking_type=3)
        admission_bookings = AdmissionsBooking.objects.filter(created__date=_date).exclude(booking_type=3)

        history_bookings = BookingHistory.objects.filter(created__date=_date).exclude(booking__booking_type=3)

        strIO = StringIO()
        fieldnames = ['Date','Confirmation Number','Name','Invoice Total','Override Reason','Override Details','Invoice','Booking Type','Created By']
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

            reason_text = ''
            if b.override_reason:
                 reason_text = b.override_reason.text 
            writer.writerow([created.strftime('%d/%m/%Y %H:%M:%S'),b.confirmation_number,b_name.encode('utf-8'),b.active_invoice.amount if b.active_invoice else '',reason_text,b.override_reason_info,b.active_invoice.reference if b.active_invoice else '', types[b.booking_type] if b.booking_type in types else b.booking_type, created_by])

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
