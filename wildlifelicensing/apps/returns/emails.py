import logging

from django.core.urlresolvers import reverse
from django.conf import settings

from wildlifelicensing.apps.emails.emails import TemplateEmailBase

logger = logging.getLogger(__name__)


class ReturnOverdueNotificationEmail(TemplateEmailBase):
    subject = 'Your wildlife licence return is overdue.'
    html_template = 'wl/emails/overdue_return_notification.html'
    txt_template = 'wl/emails/overdue_return_notification.txt'


def send_return_overdue_email_notification(ret):
    email = ReturnOverdueNotificationEmail()
    url = 'http:' + reverse('wl_returns:enter_return', args=(ret.pk,))

    context = {
        'url': url,
        'return': ret
    }

    if ret.proxy_customer is not None:
        email = ret.proxy_customer.email
    else:
        email = ret.licence.profile.email

    email.send(email, context=context)


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

    email.send(settings.WILDLIFELICENSING_EMAIL_CATCHALL, context=context)
