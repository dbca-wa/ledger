import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings
from ledger.payments.pdf import create_invoice_pdf_bytes
from ledger.payments.models import Invoice
from wildlifecompliance.components.main.utils import get_choice_value
from wildlifecompliance.components.emails.emails import TemplateEmailBase
import os

logger = logging.getLogger(__name__)

SYSTEM_NAME = 'Wildlife Licensing Automated Message'


class CallEmailForwardNotificationEmail(TemplateEmailBase):
    subject = 'Forwarded Call/Email'
    html_template = 'wildlifecompliance/emails/send_call_email_forward_notification.html'
    txt_template = 'wildlifecompliance/emails/send_call_email_forward_notification.txt'


def prepare_attachments(attachments):
    returned_attachments = []
    for document in attachments.all():
        path, filename = os.path.split(document._file.name)    
        returned_attachments.append(
            (filename, document._file.read())
        )
    return returned_attachments

def send_call_email_forward_email(select_group, call_email, attachments, request=None):
    email = CallEmailForwardNotificationEmail()
    url = request.build_absolute_uri(
        reverse(
            'internal-call-email-detail',
            kwargs={
                'call_email_id': call_email.id}))
    context = {
        'url': url,
        'call_email': call_email,
    }
    email_group = [item.email for item in select_group]
    for document in attachments.all():
        print(document._file.name)
    # email_group = 'main@localhost.com'
    msg = email.send(email_group, 
        context=context,
        attachments= 
        prepare_attachments(attachments)
        )
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    # sender = 'main@localhost.com'
    _log_call_email_comms(msg, call_email, sender=sender)

def _log_call_email_comms(email_message, call_email, sender=None):
    from wildlifecompliance.components.call_email.models import ComplianceLogEntry
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        print("call_email")
        print(call_email)
        # TODO this will log the plain text body, should we log the html
        # instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_text(sender) if sender else smart_text(
            email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ','
        # comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(all_ccs)

    # else:
    #     text = smart_text(email_message)
    #     subject = ''
    #     to = application.submitter.email
    #     fromm = smart_text(sender) if sender else SYSTEM_NAME
    #     all_ccs = ''

    kwargs = {
        'subject': subject,
        'text': text,
        'call_email': call_email,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = ComplianceLogEntry.objects.create(**kwargs)

    return email_entry
