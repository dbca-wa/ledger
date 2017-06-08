import logging

from django.core.urlresolvers import reverse

from disturbance.components.emails.emails import TemplateEmailBase

logger = logging.getLogger(__name__)


class OrganisationRequestAcceptNotificationEmail(TemplateEmailBase):
    subject = 'Your organisation request has been accepted.'
    html_template = 'disturbance/emails/organisation_request_accept_notification.html'
    txt_template = 'disturbance/emails/organisation_request_accept_notification.txt'

class OrganisationRequestDeclineNotificationEmail(TemplateEmailBase):
    subject = 'Your organisation request has been declined.'
    html_template = 'wl/emails/organisation_request_decline_notification.html'
    txt_template = 'wl/emails/organisation_request_decline_notification.txt'

def send_organisation_request_accept_email_notification(request):
    email = OrganisationRequestAcceptNotificationEmail()

    context = {
        'request': request
    }

    email.send(request.requester.email, context=context)

def send_organisation_request_decline_email_notification(request):
    email = OrganisationRequestDeclineNotificationEmail()

    context = {
        'request': request
    }

    email.send(request.requester.email, context=context)
