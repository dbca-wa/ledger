import logging

from django_hosts import reverse as hosts_reverse

from wildlifelicensing.apps.emails.emails import TemplateEmailBase

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
