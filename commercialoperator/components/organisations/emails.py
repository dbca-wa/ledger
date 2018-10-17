import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings

from commercialoperator.components.emails.emails import TemplateEmailBase

logger = logging.getLogger(__name__)

SYSTEM_NAME = settings.SYSTEM_NAME_SHORT + ' Automated Message'
class OrganisationRequestAcceptNotificationEmail(TemplateEmailBase):
    subject = 'Your organisation request has been accepted.'
    html_template = 'commercialoperator/emails/organisation_request_accept_notification.html'
    txt_template = 'commercialoperator/emails/organisation_request_accept_notification.txt'

class OrganisationAccessGroupRequestAcceptNotificationEmail(TemplateEmailBase):
    subject = 'New organisation request has been submitted.'
    html_template = 'commercialoperator/emails/org_access_group_request_accept_notification.html'
    txt_template = 'commercialoperator/emails/org_access_group_request_accept_notification.txt'

class OrganisationRequestDeclineNotificationEmail(TemplateEmailBase):
    subject = 'Your organisation request has been declined.'
    html_template = 'commercialoperator/emails/organisation_request_decline_notification.html'
    txt_template = 'commercialoperator/emails/organisation_request_decline_notification.txt'

class OrganisationLinkNotificationEmail(TemplateEmailBase):
    subject = 'You have been linked to an organisation.'
    html_template = 'commercialoperator/emails/organisation_link_notification.html'
    txt_template = 'commercialoperator/emails/organisation_link_notification.txt'

class OrganisationUnlinkNotificationEmail(TemplateEmailBase):
    subject = 'You have been unlinked from an organisation.'
    html_template = 'commercialoperator/emails/organisation_unlink_notification.html'
    txt_template = 'commercialoperator/emails/organisation_unlink_notification.txt'

def send_organisation_link_email_notification(linked_user,linked_by,organisation,request):
    email = OrganisationLinkNotificationEmail()

    context = {
        'user': linked_user,
        'linked_by': linked_by,
        'organisation': organisation
    }

    msg = email.send(linked_user.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_org_email(msg, organisation, linked_user, sender=sender)

def send_organisation_unlink_email_notification(unlinked_user,unlinked_by,organisation,request):
    email = OrganisationUnlinkNotificationEmail()

    context = {
        'user': unlinked_user,
        'unlinked_by': unlinked_by,
        'organisation': organisation
    }

    msg = email.send(unlinked_user.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_org_email(msg, organisation, unlinked_user, sender=sender)

def send_organisation_request_accept_email_notification(org_request,organisation,request):
    email = OrganisationRequestAcceptNotificationEmail()

    context = {
        'request': org_request
    }

    msg = email.send(org_request.requester.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_org_request_email(msg, org_request, sender=sender)
    _log_org_email(msg, organisation, org_request.requester, sender=sender)

def send_org_access_group_request_accept_email_notification(org_request, request, recipient_list):
    email = OrganisationAccessGroupRequestAcceptNotificationEmail()

    url = request.build_absolute_uri('/internal/organisations/access/{}'.format(org_request.id))
    if "-internal" not in url:
        url = '-internal.{}'.format(settings.SITE_DOMAIN).join(url.split('.' + settings.SITE_DOMAIN))

    context = {
        'name': request.data.get('name'),
        'abn': request.data.get('abn'),
        'url': url,
    }

    msg = email.send(recipient_list, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_org_request_email(msg, org_request, sender=sender)

    # commenting out because Organisation does not yet exist - only OrganisationRequest exists
    #_log_org_email(msg, organisation, org_request.requester, sender=sender) 


def send_organisation_request_decline_email_notification(org_request,request):
    email = OrganisationRequestDeclineNotificationEmail()

    context = {
        'request': org_request
    }

    msg = email.send(org_request.requester.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_org_request_email(msg, org_request, sender=sender)
    #_log_org_email(msg, organisation, org_request.requester, sender=sender)

def _log_org_request_email(email_message, request, sender=None):
    from commercialoperator.components.organisations.models import OrganisationRequestLogEntry
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

def _log_org_email(email_message, organisation, customer ,sender=None):
    from commercialoperator.components.organisations.models import OrganisationLogEntry
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
