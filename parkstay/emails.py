from django.conf import settings

from ledger.emails.emails import EmailBase

class TemplateEmailBase(EmailBase):
    subject = ''
    html_template = 'ps/emails/base_email.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'ps/emails/base-email.txt'

def send_booking_confirmation(booking):
    email = booking.customer.email

