import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings

from disturbance.components.emails.emails import TemplateEmailBase

logger = logging.getLogger(__name__)

SYSTEM_NAME = 'VIA Automated Message'
class OrganisationRequestAcceptNotificationEmail(TemplateEmailBase):
    subject = 'Your organisation request has been accepted.'
    html_template = 'disturbance/emails/organisation_request_accept_notification.html'
    txt_template = 'disturbance/emails/organisation_request_accept_notification.txt'

class OrganisationRequestDeclineNotificationEmail(TemplateEmailBase):
    subject = 'Your organisation request has been declined.'
    html_template = 'wl/emails/organisation_request_decline_notification.html'
    txt_template = 'wl/emails/organisation_request_decline_notification.txt'

def send_organisation_request_accept_email_notification(org_request,request):
    email = OrganisationRequestAcceptNotificationEmail()

    context = {
        'request': org_request
    }

    msg = email.send(org_request.requester.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_email(msg, org_request, sender=sender)

def send_organisation_request_decline_email_notification(org_request,request):
    email = OrganisationRequestDeclineNotificationEmail()

    context = {
        'request': org_request
    }

    msg = email.send(org_request.requester.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_email(msg, org_request, sender=sender)

def _log_email(email_message, request, sender=None):
    from disturbance.components.organisations.models import OrganisationRequestLogEntry
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_text(sender) if sender else smart_text(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ',' comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ''
        to = request.requester.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = request.requester

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'request': request,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = OrganisationRequestLogEntry.objects.create(**kwargs)

    return email_entry
