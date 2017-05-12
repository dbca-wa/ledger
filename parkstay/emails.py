from io import BytesIO

from django.conf import settings

from parkstay import pdf
from ledger.payments.pdf import create_invoice_pdf_bytes
from ledger.payments.models import Invoice

from ledger.emails.emails import EmailBase

camground_email = settings.CAMPGROUNDS_EMAIL
class TemplateEmailBase(EmailBase):
    subject = ''
    html_template = 'ps/email/base_email.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'ps/email/base_email.txt'


def send_booking_invoice(booking):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your booking invoice for {}'.format(booking.campground.name)
    email_obj.html_template = 'ps/email/invoice.html'
    email_obj.txt_template = 'ps/email/invoice.txt'

    email = booking.customer.email

    context = {
        'booking': booking
    }
    filename = 'invoice-{}({}-{}).pdf'.format(booking.campground.name,booking.arrival,booking.departure)
    references = [b.invoice_reference for b in booking.invoices.all()]
    invoice = Invoice.objects.filter(reference__in=references).order_by('-created')[0]
        
    invoice_pdf = create_invoice_pdf_bytes(filename,invoice)

    email_obj.send([email], from_address=camground_email, context=context, attachments=[(filename, invoice_pdf, 'application/pdf')])

def send_booking_confirmation(booking):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your booking confirmation for {}'.format(booking.campground.name)
    email_obj.html_template = 'ps/email/confirmation.html'
    email_obj.txt_template = 'ps/email/confirmation.txt'

    email = booking.customer.email

    context = {
        'booking': booking
    }

    att = BytesIO()
    pdf.create_confirmation(att, booking)
    att.seek(0)

    email_obj.send([email], from_address=camground_email, context=context, attachments=[('confirmation-PS{}.pdf'.format(booking.id), att.read(), 'application/pdf')])
    booking.confirmation_sent = True
    booking.save()


def send_booking_lapse(booking):
    email_obj = TemplateEmailBase()
    email_obj.subject = 'Your booking for {} has expired'.format(booking.campground.name)
    email_obj.html_template = 'ps/email/lapse.html'
    email_obj.txt_template = 'ps/email/lapse.txt'

    email = booking.customer.email

    context = {
        'booking': booking,
        'settings': settings,
    }
    email_obj.send([email], context=context)

