from io import BytesIO

from django.conf import settings

from mooring import pdf
from mooring.models import MooringsiteBooking, AdmissionsBooking, AdmissionsLine, AdmissionsLocation
#from ledger.payments.pdf import create_invoice_pdf_bytes
from mooring.invoice_pdf import create_invoice_pdf_bytes
from ledger.payments.models import Invoice
from mooring import settings 
from mooring.helpers import is_inventory, is_admin
from django.core.mail import EmailMessage, EmailMultiAlternatives

from ledger.emails.emails import EmailBase
from django.template.loader import render_to_string, get_template
from confy import env
from django.template import Context
from ledger.accounts.models import Document
from django.contrib.auth.models import Group
from ledger.accounts.models import EmailUser

import datetime
import hashlib

default_from_email = settings.DEFAULT_FROM_EMAIL
default_campground_email = settings.CAMPGROUNDS_EMAIL
default_rottnest_email = settings.ROTTNEST_EMAIL

class TemplateEmailBase(EmailBase):
    subject = ''
    html_template = 'mooring/email/base_email.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'mooring/email/base_email.txt'

def sendHtmlEmail(to,subject,context,template,cc,bcc,from_email,template_group,attachments=None):

    email_delivery = env('EMAIL_DELIVERY', 'off')
    override_email = env('OVERRIDE_EMAIL', None)
    context['default_url'] = env('DEFAULT_HOST', '')
    context['default_url_internal'] = env('DEFAULT_URL_INTERNAL', '')
    log_hash = int(hashlib.sha1(str(datetime.datetime.now())).hexdigest(), 16) % (10 ** 8)

    if email_delivery != 'on':
        print ("EMAIL DELIVERY IS OFF NO EMAIL SENT -- email.py ")
        return False

    if template is None:
        raise ValidationError('Invalid Template')
    if to is None:
        raise ValidationError('Invalid Email')
    if subject is None:
        raise ValidationError('Invalid Subject')

    if from_email is None:
        if settings.DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL
        else:
            from_email = 'no-reply@dbca.wa.gov.au'

    context['version'] = settings.VERSION_NO
    # Custom Email Body Template
    context['body'] = get_template(template).render(Context(context))
    # Main Email Template Style ( body template is populated in the center
    if template_group == 'rottnest':
        main_template = get_template('mooring/email/base_email-rottnest.html').render(Context(context))
    elif template_group == 'system-oim':
        main_template = get_template('mooring/email/base_email-oim.html').render(Context(context))
    else:
        main_template = get_template('mooring/email/base_email2.html').render(Context(context))
   
    reply_to=None

    if attachments is None:
        attachments = []

    # Convert Documents to (filename, content, mime) attachment
    _attachments = []
    for attachment in attachments:
        if isinstance(attachment, Document):
             filename = str(attachment)
             content = attachment.file.read()
             mime = mimetypes.guess_type(attachment.filename)[0]
             _attachments.append((filename, content, mime))
        else:
             _attachments.append(attachment)


    if override_email is not None:
        to = override_email.split(",")
        if cc:
            cc = override_email.split(",")
        if bcc:
            bcc = override_email.split(",")

    if len(to) > 1:
        msg = EmailMultiAlternatives(subject, "Please open with a compatible html email client.", from_email=from_email, to=to, attachments=_attachments, cc=cc, bcc=bcc, reply_to=reply_to)
        msg.attach_alternative(main_template, 'text/html')

        #msg = EmailMessage(subject, main_template, to=[to_email],cc=cc, from_email=from_email)
        #msg.content_subtype = 'html'
        #if attachment1:
        #    for a in attachment1:
        #        msg.attach(a)
        try:
             email_log(str(log_hash)+' '+subject)
             msg.send()
             email_log(str(log_hash)+' Successfully sent to mail gateway')
        except Exception as e:
                email_log(str(log_hash)+' Error Sending - '+str(e))

    else:
          msg = EmailMultiAlternatives(subject, "Please open with a compatible html email client.", from_email=from_email, to=to, attachments=_attachments, cc=cc, bcc=bcc, reply_to=reply_to)
          msg.attach_alternative(main_template, 'text/html')

          #msg = EmailMessage(subject, main_template, to=to,cc=cc, from_email=from_email)
          #msg.content_subtype = 'html'
          #if attachment1:
          #    for a in attachment1:
          #        msg.attach(a)
          try:
               email_log(str(log_hash)+' '+subject) 
               msg.send()
               email_log(str(log_hash)+' Successfully sent to mail gateway')
          except Exception as e:
               email_log(str(log_hash)+' Error Sending - '+str(e))


    return True



def send_admissions_booking_invoice(admissionsBooking, request, context_processor):
    email_obj = TemplateEmailBase()
    admissionsLine = AdmissionsLine.objects.get(admissionsBooking=admissionsBooking)
    template = 'mooring/email/admissions_invoice.html'

    cc = None
    bcc = None
    from_email = None
    to = admissionsBooking.customer.email
    subject = 'Admission fee payment invoice for {}'.format(admissionsLine.arrivalDate)

    #email_obj.subject = 'Admission fee payment invoice for {}'.format(admissionsLine.arrivalDate)
    #email_obj.html_template = 'mooring/email/admissions_invoice.html'
    #email_obj.txt_template = 'mooring/email/admissions_invoice.txt'
    #email = admissionsBooking.customer.email

    context = {
        'booking': admissionsBooking,
        'arrivalDate': admissionsLine.arrivalDate,
        'context_processor': context_processor
    }
    filename = 'invoice-{}({}).pdf'.format(admissionsLine.arrivalDate, admissionsBooking.customer.get_full_name())
    references = [b.invoice_reference for b in admissionsBooking.invoices.all()]
    invoice = Invoice.objects.filter(reference__in=references).order_by('-created')[0]
#    invoice_pdf = create_invoice_pdf_bytes(filename,invoice)
    invoice_pdf = create_invoice_pdf_bytes(filename,invoice, request, context_processor)
#    rottnest_email = default_rottnest_email
#    rottnest_email = default_from_email
    template_group = context_processor['TEMPLATE_GROUP']
    sendHtmlEmail([to],subject,context,template,cc,bcc,from_email,template_group,attachments=[(filename, invoice_pdf, 'application/pdf')])

#    email_obj.send([email], from_address=rottnest_email, context=context, attachments=[(filename, invoice_pdf, 'application/pdf')])


def send_booking_invoice(booking,request, context_processor):

    subject = 'Your booking invoice'
    template = 'mooring/email/booking_invoice.html'
    cc = None
    bcc = None
    from_email = None
    context= {'booking': booking, 'context_processor': context_processor}
    to = booking.customer.email

    filename = 'invoice-{}({}-{}).pdf'.format(booking.mooringarea.name,booking.arrival,booking.departure)
    references = [b.invoice_reference for b in booking.invoices.all()]
    invoice = Invoice.objects.filter(reference__in=references).order_by('-created')[0]
    invoice_pdf = create_invoice_pdf_bytes(filename,invoice, request, context_processor)
    template_group = context_processor['TEMPLATE_GROUP']
    sendHtmlEmail([to],subject,context,template,cc,bcc,from_email,template_group,attachments=[(filename, invoice_pdf, 'application/pdf')])


def send_booking_invoice_old(booking, request, context_processor):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your booking invoice for {}'.format(booking.mooringarea.name)
    email_obj.html_template = 'mooring/email/invoice.html'
    email_obj.txt_template = 'mooring/email/invoice.txt'

    email = booking.customer.email

    context = {
        'booking': booking,
        'context_processor': context_processor
    }
    filename = 'invoice-{}({}-{}).pdf'.format(booking.mooringarea.name,booking.arrival,booking.departure)
    references = [b.invoice_reference for b in booking.invoices.all()]
    invoice = Invoice.objects.filter(reference__in=references).order_by('-created')[0]
        
    invoice_pdf = create_invoice_pdf_bytes(filename,invoice, request, context_processor)

#    campground_email = booking.mooringarea.email if booking.mooringarea.email else default_campground_email
    campground_email = default_from_email 
    email_obj.send([email], from_address=campground_email, context=context, attachments=[(filename, invoice_pdf, 'application/pdf')])

def send_admissions_booking_confirmation(admissionsBooking, request, context_processor):
    email_obj = TemplateEmailBase()

    admissionsLine = AdmissionsLine.objects.get(admissionsBooking=admissionsBooking)
    subject = 'Admission Fee Payment Confirmation {} on {}'.format(admissionsBooking.confirmation_number,admissionsLine.arrivalDate)
    template = 'mooring/email/admissions_confirmation.html'
    cc = None
    bcc = None
    from_email = None
    template_group = context_processor['TEMPLATE_GROUP']

#    email_obj.subject = 'Admission Fee Payment Confirmation {} on {}'.format(admissionsBooking.confirmation_number,admissionsLine.arrivalDate)
#    email_obj.html_template = 'mooring/email/admissions_confirmation.html'
#    email_obj.txt_template = 'mooring/email/admissions_confirmation.txt'
    email = admissionsBooking.customer.email
    #bcc = [default_rottnest_email]
#    rottnest_email = default_rottnest_email
    #rottnest_email = default_from_email
    my_bookings_url = context_processor['PUBLIC_URL']+'/mybookings/'

    context = {
        'booking': admissionsBooking,
        'my_bookings': my_bookings_url,
        'context_processor': context_processor
    }
    att = BytesIO()
    pdf.create_admissions_confirmation(att, admissionsBooking, context_processor)
    att.seek(0)
#    filename = 'confirmation-AD{}({}).pdf'.format(admissionsBooking.id, admissionsBooking.customer.get_full_name())
#    email_obj.send([email], from_address=rottnest_email, context=context, cc=cc, bcc=bcc, attachments=[(filename, att.read(), 'application/pdf')])

    sendHtmlEmail([email],subject,context,template,cc,bcc,from_email,template_group,attachments=[('confirmation-AD{}.pdf'.format(admissionsBooking.id), att.read(), 'application/pdf')])

def send_booking_confirmation(booking,request,context_processor):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your booking {} at {} is confirmed'.format(booking.confirmation_number,booking.mooringarea.name)
    email_obj.html_template = 'mooring/email/confirmation.html'
    email_obj.txt_template = 'mooring/email/confirmation.txt'
    from_email = None
    email = booking.customer.email

    template = 'mooring/email/booking_confirmation.html'

    cc = None
    bcc = [default_campground_email]
    template_group = context_processor['TEMPLATE_GROUP']

    #campground_email = booking.mooringarea.email if booking.mooringarea.email else default_campground_email
    campground_email = default_from_email
    if campground_email != default_campground_email:
        cc = [campground_email]

    my_bookings_url = context_processor['PUBLIC_URL']+'/mybookings/'
    #booking_availability = request.build_absolute_uri('/availability/?site_id={}'.format(booking.mooringarea.id))
    unpaid_vehicle = False
    mobile_number = booking.customer.mobile_number
    booking_number = booking.details.get('phone',None)
    phone_number = booking.customer.phone_number
    tel = None

    if booking_number:
        tel = booking_number
    elif mobile_number:
        tel = mobile_number
    else:
        tel = phone_number
    tel = tel if tel else ''

    for v in booking.vehicle_payment_status:
        if v.get('Paid') == 'No':
            unpaid_vehicle = True
            break
    additional_info = booking.mooringarea.additional_info if booking.mooringarea.additional_info else ''

    msbs = MooringsiteBooking.objects.filter(booking=booking)
    contact_list = []
    moorings = []
    for m in msbs:
        if m.campsite.mooringarea not in moorings:
            moorings.append(m.campsite.mooringarea)
            contact = m.campsite.mooringarea.contact
            if not any(c['email'] == contact.email for c in contact_list) or not any(c['phone'] == contact.phone_number for c in contact_list):
                line = {'moorings': m.campsite.mooringarea.name, 'email': contact.email, 'phone': contact.phone_number}
                contact_list.append(line)
            else:
                index = next((index for (index, d) in enumerate(contact_list) if d['email'] == contact.email), None)
                contact_list[index]['moorings'] += ', ' + m.campsite.mooringarea.name


    context = {
        'booking': booking,
        'phone_number': tel,
        'campground_email': campground_email,
        'my_bookings': my_bookings_url,
        #'availability': booking_availability,
        'unpaid_vehicle': unpaid_vehicle,
        'additional_info': additional_info,
        'contact_list': contact_list,
        'context_processor': context_processor
    }

    att = BytesIO()
    mooring_booking = []
    if MooringsiteBooking.objects.filter(booking=booking).count() > 0:
        mooring_booking = MooringsiteBooking.objects.filter(booking=booking)
    pdf.create_confirmation(att, booking, mooring_booking,context_processor)
    att.seek(0) 
    subject = "Your mooring booking confirmation"
    if booking.admission_payment:
        subject = "Your mooring booking and admissions confirmation"
        att2 = BytesIO()
        admissionsBooking = AdmissionsBooking.objects.get(id=booking.admission_payment.id)
        pdf.create_admissions_confirmation(att2, admissionsBooking, context_processor)
        att2.seek(0)
        filename = 'confirmation-AD{}.pdf'.format(admissionsBooking.id)
        sendHtmlEmail([email],subject,context,template,cc,bcc,from_email,template_group,attachments=[('confirmation-PS{}.pdf'.format(booking.id), att.read(), 'application/pdf'), (filename, att2.read(), 'application/pdf')])
        #email_obj.send([email], from_address=campground_email, context=context, cc=cc, bcc=bcc, attachments=[('confirmation-PS{}.pdf'.format(booking.id), att.read(), 'application/pdf'), (filename, att2.read(), 'application/pdf')])
    else:
        #email_obj.send([email], from_address=campground_email, context=context, cc=cc, bcc=bcc, attachments=[('confirmation-PS{}.pdf'.format(booking.id), att.read(), 'application/pdf')])
        sendHtmlEmail([email],subject,context,template,cc,bcc,from_email,template_group,attachments=[('confirmation-PS{}.pdf'.format(booking.id), att.read(), 'application/pdf')])
    booking.confirmation_sent = True
    booking.save()


def send_booking_cancelation(booking,request):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Cancelled: your booking {} at {},{}.'.format(booking.confirmation_number,booking.mooringarea.name,booking.mooringarea.park.name)
    email_obj.html_template = 'mooring/email/cancel.html'
    email_obj.txt_template = 'mooring/email/cancel.txt'

    email = booking.customer.email

    bcc = [default_campground_email]

    #campground_email = booking.mooringarea.email if booking.mooringarea.email else default_campground_email
    campground_email = default_from_email
    my_bookings_url = '{}mybookings/'.format(settings.PARKSTAY_EXTERNAL_URL)
    context = {
        'booking': booking,
        'my_bookings': my_bookings_url,
        'campground_email': campground_email
    }

    email_obj.send([email], from_address=campground_email, cc=[campground_email], bcc=bcc, context=context)

def send_booking_lapse(booking):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your booking for {} has expired'.format(booking.campground.name)
    email_obj.html_template = 'mooring/email/lapse.html'
    email_obj.txt_template = 'mooring/email/lapse.txt'

    email = booking.customer.email

    context = {
        'booking': booking,
        'settings': settings,
    }
    email_obj.send([email], from_address=default_from_email, context=context)

def send_booking_period_email(moorings, group, days):
    email_obj = TemplateEmailBase()
    email_obj.subject = "Moorings with Booking Period Gaps"
    email_obj.html_template = 'mooring/email/bpemail.html'
    email_obj.txt_template = 'mooring/email/bpemail.txt'

    members = group.members.all()
    emails = []
    if not settings.PRODUCTION_EMAIL:
        emails.append(settings.NON_PROD_EMAIL)
    else:
        for mem in members:
            if is_inventory(mem):
                emails.append(mem.email)

    context = {
        'moorings': moorings,
        'days': days
    }
    email_obj.send(emails, from_address=default_from_email, context=context)

### Admission Emails
def send_refund_failure_email_admissions(booking, context_processor):

    subject = 'Failed to refund for {}, requires manual intervention.'.format(booking)
    template = 'mooring/email/refund_failed_admissions.html'
    cc = None
    bcc = None
    from_email = None
    context= {'booking': booking, 'context_processor': context_processor}
    template_group = context_processor['TEMPLATE_GROUP']
    if not settings.PRODUCTION_EMAIL:
       to = settings.NON_PROD_EMAIL
       sendHtmlEmail([to],subject,context,template,cc,bcc,from_email,template_group,attachments=None)
    else:
       pa = Group.objects.get(name='Payments Officers')
       ma = Group.objects.get(name="Mooring Admin")
       user_list = EmailUser.objects.filter(groups__in=[ma,]).distinct()

       for u in user_list:
          to = u.email
          sendHtmlEmail([to],subject,context,template,cc,bcc,from_email,template_group,attachments=None)


def send_refund_completed_email_customer_admissions(booking, context_processor):
    subject = 'Your refund for booking {} was completed.'.format(booking.id)
    template = 'mooring/email/refund_completed_customer_admissions.html'
    cc = None
    bcc = None
    from_email = None
    context= {'booking': booking, 'context_processor': context_processor}
    to = booking.customer.email
    template_group = context_processor['TEMPLATE_GROUP']
    sendHtmlEmail([to],subject,context,template,cc,bcc,from_email,template_group,attachments=None)

def send_refund_failure_email_customer_admissions(booking, context_processor):

    subject = 'Your refund for booking has failed {}.'.format(booking.id)
    template = 'mooring/email/refund_failed_customer_admissions.html'
    cc = None
    bcc = None
    from_email = None
    context= {'booking': booking, 'context_processor': context_processor}
    to = booking.customer.email
    template_group = context_processor['TEMPLATE_GROUP']
    sendHtmlEmail([to],subject,context,template,cc,bcc,from_email,template_group,attachments=None)
####

def send_refund_failure_email(booking, context_processor):

    subject = 'Failed to refund for {}, requires manual intervention.'.format(booking)
    template = 'mooring/email/refund_failed.html'
    cc = None
    bcc = None
    from_email = None
    context= {'booking': booking, 'context_processor': context_processor}
    template_group = context_processor['TEMPLATE_GROUP']
    if not settings.PRODUCTION_EMAIL:
       to = settings.NON_PROD_EMAIL
       sendHtmlEmail([to],subject,context,template,cc,bcc,from_email,template_group,attachments=None)
    else:

       pa = Group.objects.get(name='Payments Officers')
       ma = Group.objects.get(name="Mooring Admin")
       user_list = EmailUser.objects.filter(groups__in=[ma,]).distinct()

       for u in user_list:
          to = u.email
          sendHtmlEmail([to],subject,context,template,cc,bcc,from_email,template_group,attachments=None)


def send_refund_completed_email_customer(booking, context_processor):
    subject = 'Your refund for booking {} was completed.'.format(booking.id)
    template = 'mooring/email/refund_completed_customer.html'
    cc = None
    bcc = None
    from_email = None
    context= {'booking': booking, 'context_processor': context_processor}
    to = booking.customer.email
    template_group = context_processor['TEMPLATE_GROUP']
    sendHtmlEmail([to],subject,context,template,cc,bcc,from_email,template_group,attachments=None)

def send_refund_failure_email_customer(booking, context_processor):

    subject = 'Your refund for booking has failed {}.'.format(booking.id)
    template = 'mooring/email/refund_failed_customer.html'
    cc = None
    bcc = None
    from_email = None
    context= {'booking': booking, 'context_processor': context_processor}
    to = booking.customer.email
    template_group = context_processor['TEMPLATE_GROUP']
    sendHtmlEmail([to],subject,context,template,cc,bcc,from_email,template_group,attachments=None)

def send_booking_cancellation_email_customer(booking, context_processor):

    subject = 'Your booking with ref {} has been cancelled.'.format(booking.id)
    template = 'mooring/email/booking_cancelled_customer.html'
    cc = None
    bcc = None
    from_email = None
    context= {'booking': booking, 'context_processor': context_processor}
    to = booking.customer.email
    template_group = context_processor['TEMPLATE_GROUP']
    sendHtmlEmail([to],subject,context,template,cc,bcc,from_email,template_group,attachments=None)

def send_refund_failure_email_old(booking):
    email_obj = TemplateEmailBase2()
    email_obj.subject = 'Failed to refund for {}, requires manual intervention.'.format(booking)
    email_obj.html_template = 'mooring/email/refund_failed.html'
    email_obj.txt_template = 'mooring/email/refund_failed.txt'

    # email = booking.customer.email
    email = 'jason.moore@dbca.wa.gov.au'
    context = {
        'booking': booking,
    }

    pa = Group.objects.get(name='Payments Officers')
    ma = Group.objects.get(name="Mooring Admin")
    user_list = EmailUser.objects.filter(groups__in=[ma,]).distinct()

    ### REMOVE ###
    for u in user_list:
       email = u.email
       email_obj.send([email], from_address=default_from_email, context=context)
    ### REM<O ####
    if not settings.PRODUCTION_EMAIL:
       email = settings.NON_PROD_EMAIL
       email_obj.send([email], from_address=default_from_email, context=context)
    else:
       for u in user_list:
          email = u.email
          email_obj.send([email], from_address=default_from_email, context=context)

def send_registered_vessels_email(content):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Lotus notes extract run.'
    email_obj.html_template = 'mooring/email/reg_ves.html'
    email_obj.txt_template = 'mooring/email/reg_ves.txt'

#    if not settings.PRODUCTION_EMAIL:
#        emails.append(settings.NON_PROD_EMAIL)
#    else:
    emails = []
    admin_emails = settings.NOTIFICATION_EMAIL
    ae = admin_emails.split(',')
    for i in ae:
        emails.append(i)


    loc = AdmissionsLocation.objects.filter(key='ria')
    if loc.count() > 0:
        group = loc[0].mooring_group
        if group:
            for mem in group.members.all():
                if is_admin(mem):
                    emails.append(mem.email)


     

    context = {
        'content': content
    }
    
    email_obj.send(emails, from_address=default_from_email, context=context)


def email_log(line):
     dt = datetime.datetime.now()
     f= open(settings.BASE_DIR+"/logs/email.log","a+")
     f.write(str(dt.strftime('%Y-%m-%d %H:%M:%S'))+': '+line+"\r\n")
     f.close()  


