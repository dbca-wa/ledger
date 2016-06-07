import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage

from django_hosts import reverse as hosts_reverse

from wildlifelicensing.apps.emails.emails import TemplateEmailBase
from wildlifelicensing.apps.applications.models import EmailLogEntry

logger = logging.getLogger(__name__)


class ReturnOverdueNotificationEmail(TemplateEmailBase):
    subject = 'Your wildlife licence return is overdue.'
    html_template = 'wl/emails/overdue_return_notification.html'
    txt_template = 'wl/emails/overdue_return_notification.txt'


def send_return_overdue_email_notification(ret):
    email = ReturnOverdueNotificationEmail()
    url = 'http:' + hosts_reverse('returns:enter_return', args=(ret.pk,))

    context = {
        'url': url,
        'return': ret
    }

    email.send(ret.licence.profile.email, context=context)


def _log_email(email_message, application, sender=None):
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        from_email = unicode(sender) if sender else unicode(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ';'.join(email_message.to)
        else:
            to = unicode(email_message.to)
    else:
        text = unicode(email_message)
        subject = ''
        to = application.applicant_profile.user.email
        from_email = unicode(sender) if sender else ''

    kwargs = {
        'subject': subject,
        'text': text,
        'application': application,
        'user': sender,
        'to': to,
        'from_email': from_email
    }
    email_entry = EmailLogEntry.objects.create(**kwargs)
    return email_entry
