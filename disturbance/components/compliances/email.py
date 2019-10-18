import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings

from disturbance.components.emails.emails import TemplateEmailBase
from ledger.accounts.models import EmailUser

logger = logging.getLogger(__name__)

SYSTEM_NAME = settings.SYSTEM_NAME_SHORT + ' Automated Message'
class ComplianceExternalSubmitSendNotificationEmail(TemplateEmailBase):
    subject = 'Your Compliance with requirements has been submitted.'
    html_template = 'disturbance/emails/send_external_submit_notification.html'
    txt_template = 'disturbance/emails/send_external_submit_notification.txt'

class ComplianceSubmitSendNotificationEmail(TemplateEmailBase):
    subject = 'A new Compliance has been submitted.'
    html_template = 'disturbance/emails/send_submit_notification.html'
    txt_template = 'disturbance/emails/send_submit_notification.txt'

class ComplianceAcceptNotificationEmail(TemplateEmailBase):
    subject = 'Your Compliance with requirements has been accepted.'
    html_template = 'disturbance/emails/compliance_accept_notification.html'
    txt_template = 'disturbance/emails/compliance_accept_notification.txt'

class ComplianceAmendmentRequestSendNotificationEmail(TemplateEmailBase):
    subject = 'An amendment to your Compliance with requirements is required.'
    html_template = 'disturbance/emails/send_amendment_notification.html'
    txt_template = 'disturbance/emails/send_amendment_notification.txt'

class ComplianceReminderNotificationEmail(TemplateEmailBase):
    subject = 'Your Compliance with requirements has passed the due date.'
    html_template = 'disturbance/emails/send_reminder_notification.html'
    txt_template = 'disturbance/emails/send_reminder_notification.txt'

class ComplianceInternalReminderNotificationEmail(TemplateEmailBase):
    subject = 'A Compliance with requirements has passed the due date.'
    html_template = 'disturbance/emails/send_internal_reminder_notification.html'
    txt_template = 'disturbance/emails/send_internal_reminder_notification.txt'

class ComplianceDueNotificationEmail(TemplateEmailBase):
    subject = 'Your Compliance with requirements is due for submission.'
    html_template = 'disturbance/emails/send_due_notification.html'
    txt_template = 'disturbance/emails/send_due_notification.txt'

class ComplianceInternalDueNotificationEmail(TemplateEmailBase):
    subject = 'A Compliance with requirements is due for submission.'
    html_template = 'disturbance/emails/send_internal_due_notification.html'
    txt_template = 'disturbance/emails/send_internal_due_notification.txt'

def send_amendment_email_notification(amendment_request, request, compliance):
    email = ComplianceAmendmentRequestSendNotificationEmail()
    #reason = amendment_request.get_reason_display()
    reason = amendment_request.reason.reason
    url = request.build_absolute_uri(reverse('external-compliance-detail',kwargs={'compliance_pk': compliance.id}))
    url = ''.join(url.split('-internal'))
    context = {
        'compliance': compliance,
        'reason': reason,
        'amendment_request_text': amendment_request.text,
        'url': url
    }

    all_ccs = []
    if compliance.proposal.applicant.email:
        cc_list = compliance.proposal.applicant.email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(compliance.submitter.email, cc=all_ccs, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL  
    _log_compliance_email(msg, compliance, sender=sender)
    _log_org_email(msg, compliance.proposal.applicant, compliance.submitter, sender=sender)


#send reminder emails if Compliance has not been lodged by due date. Used in Cron job so cannot use 'request' parameter
def send_reminder_email_notification(compliance):
    """ Used by the management command, therefore have no request object - therefore explicitly defining base_url """
    email = ComplianceReminderNotificationEmail()
    #url = request.build_absolute_uri(reverse('external-compliance-detail',kwargs={'compliance_pk': compliance.id}))
    url=settings.SITE_URL if settings.SITE_URL else ''
    url+=reverse('external-compliance-detail',kwargs={'compliance_pk': compliance.id})
    context = {
        'compliance': compliance,
        'url': url
    }
    all_ccs = []
    if compliance.proposal.applicant.email:
        cc_list = compliance.proposal.applicant.email
        if cc_list:
            all_ccs = [cc_list]

    submitter = compliance.submitter.email if compliance.submitter and compliance.submitter.email else compliance.proposal.submitter.email
    msg = email.send(submitter, cc=all_ccs, context=context)
    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        sender_user = EmailUser.objects.create(email=sender, password='')
    _log_compliance_email(msg, compliance, sender=sender_user)
    _log_org_email(msg, compliance.proposal.applicant, compliance.submitter, sender=sender_user)

def send_internal_reminder_email_notification(compliance):
    email = ComplianceInternalReminderNotificationEmail()
    #url = request.build_absolute_uri(reverse('external-compliance-detail',kwargs={'compliance_pk': compliance.id}))
    url=settings.SITE_URL
    url+=reverse('internal-compliance-detail',kwargs={'compliance_pk': compliance.id})
    if "-internal" not in url:
        # add it. This email is for internal staff
        url = '-internal.{}'.format(settings.SITE_DOMAIN).join(url.split('.' + settings.SITE_DOMAIN))

    context = {
        'compliance': compliance,
        'url': url
    }

    msg = email.send(compliance.proposal.assessor_recipients, context=context)
    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        sender_user = EmailUser.objects.create(email=sender, password='')
    _log_compliance_email(msg, compliance, sender=sender_user)
    _log_org_email(msg, compliance.proposal.applicant, compliance.submitter, sender=sender_user)

def send_due_email_notification(compliance):
    email = ComplianceDueNotificationEmail()
    #url = request.build_absolute_uri(reverse('external-compliance-detail',kwargs={'compliance_pk': compliance.id}))
    url=settings.SITE_URL
    url+=reverse('external-compliance-detail',kwargs={'compliance_pk': compliance.id})
    context = {
        'compliance': compliance,
        'url': url
    }
    all_ccs = []
    if compliance.proposal.applicant.email:
        cc_list = compliance.proposal.applicant.email
        if cc_list:
            all_ccs = [cc_list]

    submitter = compliance.submitter.email if compliance.submitter and compliance.submitter.email else compliance.proposal.submitter.email
    msg = email.send(submitter, cc=all_ccs, context=context)
    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        sender_user = EmailUser.objects.create(email=sender, password='')
    _log_compliance_email(msg, compliance, sender=sender_user)
    _log_org_email(msg, compliance.proposal.applicant, compliance.submitter, sender=sender_user)

def send_internal_due_email_notification(compliance):
    email = ComplianceInternalDueNotificationEmail()
    #url = request.build_absolute_uri(reverse('external-compliance-detail',kwargs={'compliance_pk': compliance.id}))
    url=settings.SITE_URL
    url+=reverse('internal-compliance-detail',kwargs={'compliance_pk': compliance.id})
    if "-internal" not in url:
        # add it. This email is for internal staff
        url = '-internal.{}'.format(settings.SITE_DOMAIN).join(url.split('.' + settings.SITE_DOMAIN))

    context = {
        'compliance': compliance,
        'url': url
    }

    msg = email.send(compliance.proposal.assessor_recipients, context=context)
    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        sender_user = EmailUser.objects.create(email=sender, password='')
    _log_compliance_email(msg, compliance, sender=sender_user)
    _log_org_email(msg, compliance.proposal.applicant, compliance.submitter, sender=sender_user)


def send_compliance_accept_email_notification(compliance,request):
    email = ComplianceAcceptNotificationEmail()

    context = {
        'compliance': compliance
    }    
    all_ccs = []
    if compliance.proposal.applicant.email:
        cc_list = compliance.proposal.applicant.email
        if cc_list:
            all_ccs = [cc_list]
    msg = email.send(compliance.submitter.email, cc=all_ccs, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_compliance_email(msg, compliance, sender=sender)
    _log_org_email(msg, compliance.proposal.applicant, compliance.submitter, sender=sender)

def send_external_submit_email_notification(request, compliance):
    email = ComplianceExternalSubmitSendNotificationEmail()
    url = request.build_absolute_uri(reverse('external-compliance-detail',kwargs={'compliance_pk': compliance.id}))
    url = ''.join(url.split('-internal'))
    context = {
        'compliance': compliance,
        'submitter': compliance.submitter.get_full_name(),
        'url': url
    }
    all_ccs = []
    if compliance.proposal.applicant.email:
        cc_list = compliance.proposal.applicant.email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(compliance.submitter.email, cc=all_ccs, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_compliance_email(msg, compliance, sender=sender)
    _log_org_email(msg, compliance.proposal.applicant, compliance.submitter, sender=sender)

def send_submit_email_notification(request, compliance):
    email = ComplianceSubmitSendNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-compliance-detail',kwargs={'compliance_pk': compliance.id}))
    if "-internal" not in url:
        # add it. This email is for internal staff
        url = '-internal.{}'.format(settings.SITE_DOMAIN).join(url.split('.' + settings.SITE_DOMAIN))

    context = {
        'compliance': compliance,
        'url': url
    }

    msg = email.send(compliance.proposal.assessor_recipients, context=context)
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
