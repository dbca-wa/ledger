import logging

from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.encoding import smart_text
from django.core.mail import EmailMultiAlternatives, EmailMessage

from wildlifelicensing.apps.emails.emails import TemplateEmailBase, host_reverse
from wildlifelicensing.apps.returns.models import ReturnLogEntry

SYSTEM_NAME = 'Wildlife Licensing Automated Message'

logger = logging.getLogger(__name__)


class ReturnOverdueNotificationEmail(TemplateEmailBase):
    subject = 'Your wildlife licence return is overdue.'
    html_template = 'wl/emails/overdue_return_notification.html'
    txt_template = 'wl/emails/overdue_return_notification.txt'


def send_return_overdue_email_notification(ret):
    email = ReturnOverdueNotificationEmail()
    url = host_reverse('wl_returns:enter_return', args=(ret.pk,))

    context = {
        'url': url,
        'return': ret
    }

    if ret.proxy_customer is not None:
        recipient_email = ret.proxy_customer.email
    else:
        recipient_email = ret.licence.profile.email

    msg = email.send(recipient_email, context=context)
    _log_email(msg, ret, sender=None)


class ReturnOverdueStaffNotificationEmail(TemplateEmailBase):
    subject = 'Wildlife Licensing [{}]: overdue return'
    html_template = 'wl/emails/overdue_return_staff_notification.html'
    txt_template = 'wl/emails/overdue_return_staff_notification.txt'

    def __init__(self, ret):
        self.subject = self.subject.format(ret.licence.holder.get_full_name())


def send_return_overdue_staff_email_notification(ret):
    email = ReturnOverdueStaffNotificationEmail(ret)

    context = {
        'return': ret
    }

    email.send(settings.EMAIL_FROM, context=context)


class ReturnAmendmentRequestedEmail(TemplateEmailBase):
    subject = 'An amendment to one of your wildlife licensing return is required.'
    html_template = 'wl/emails/return_amendment_requested.html'
    txt_template = 'wl/emails/return_amendment_requested.txt'


def send_amendment_requested_email(amendment_request, request, application):
    ret = amendment_request.ret
    email = ReturnAmendmentRequestedEmail()
    url = request.build_absolute_uri(
        reverse('wl_returns:enter_return', args=[ret.pk])
    )

    context = {
        'amendment_request': amendment_request,
        'reason': amendment_request.reason,
        'url': url,
        'application': application,
    }

    if application.proxy_applicant is None:
        recipient_email = application.applicant_profile.email
    else:
        recipient_email = application.proxy_applicant.email

    msg = email.send(recipient_email, context=context)
    _log_email(msg, ret, sender=request.user)


def _log_email(email_message, ret, sender=None):
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
        to = ret.licence.holder.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = ret.licence.holder

    staff = sender

    kwargs = {
        'ret': ret,
        'type': 'email',
        'subject': subject,
        'text': text,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = ReturnLogEntry.objects.create(**kwargs)

    return email_entry
