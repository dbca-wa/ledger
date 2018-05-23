import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings

from disturbance.components.emails.emails import TemplateEmailBase

logger = logging.getLogger(__name__)

SYSTEM_NAME = 'VIA Automated Message'
class ComplianceAcceptNotificationEmail(TemplateEmailBase):
    subject = 'Your Compliance with requirements has been accepted.'
    html_template = 'disturbance/emails/compliance_accept_notification.html'
    txt_template = 'disturbance/emails/compliance_accept_notification.txt'

class ComplianceAmendmentRequestSendNotificationEmail(TemplateEmailBase):
    subject = 'An amendment to your Compliance with requirements is required.'
    html_template = 'disturbance/emails/send_amendment_notification.html'
    txt_template = 'disturbance/emails/send_amendment_notification.txt'

def send_amendment_email_notification(amendment_request, request, compliance):
    email = ComplianceAmendmentRequestSendNotificationEmail()
    reason = amendment_request.get_reason_display()
    url = request.build_absolute_uri(reverse('external-compliance-detail',kwargs={'compliance_pk': compliance.id}))
    context = {
        'compliance': compliance,
        'reason': reason,
        'amendment_request_text': amendment_request.text,
        'url': url
    }

    msg = email.send(compliance.submitter.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_compliance_email(msg, compliance, sender=sender)
    _log_org_email(msg, compliance.proposal.applicant, compliance.submitter, sender=sender)


def send_compliance_accept_email_notification(compliance,request):
    email = ComplianceAcceptNotificationEmail()

    context = {
        'compliance': compliance
    }    
    msg = email.send(compliance.submitter.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_compliance_email(msg, compliance, sender=sender)
    _log_org_email(msg, compliance.proposal.applicant, compliance.submitter, sender=sender)


def _log_compliance_email(email_message, compliance, sender=None):
    from disturbance.components.compliances.models import ComplianceLogEntry
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
        to = compliance.submitter.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = compliance.submitter

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'compliance': compliance,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = ComplianceLogEntry.objects.create(**kwargs)

    return email_entry


def _log_org_email(email_message, organisation, customer ,sender=None):
    from disturbance.components.organisations.models import OrganisationLogEntry
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
        to = customer.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = customer

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'organisation': organisation,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = OrganisationLogEntry.objects.create(**kwargs)

    return email_entry