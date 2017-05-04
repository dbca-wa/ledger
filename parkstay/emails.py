from io import BytesIO

from django.conf import settings

from parkstay import pdf

from ledger.emails.emails import EmailBase

class TemplateEmailBase(EmailBase):
    subject = ''
    html_template = 'ps/email/base_email.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'ps/email/base_email.txt'


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

    email_obj.send([email], context=context, attachments=[('confirmation-PS{}.pdf'.format(booking.id), att.read(), 'application/pdf')])
