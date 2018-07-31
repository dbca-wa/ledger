import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings

from wildlifecompliance.components.emails.emails import TemplateEmailBase

logger = logging.getLogger(__name__)

SYSTEM_NAME = 'Wildlife Compliance Automated Message'
class ReferralSendNotificationEmail(TemplateEmailBase):
    subject = 'A referral for a application has been sent to you.'
    html_template = 'wildlifecompliance/emails/applications/send_referral_notification.html'
    txt_template = 'wildlifecompliance/emails/applications/send_referral_notification.txt'


class ApplicationSubmitNotificationEmail(TemplateEmailBase):
    subject = 'A new application has been submitted.'
    html_template = 'wildlifecompliance/emails/send_application_submit_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_submit_notification.txt'

class ApplicationAmendmentRequestNotificationEmail(TemplateEmailBase):
    subject = 'An amendment has been requested for your application.'
    html_template = 'wildlifecompliance/emails/send_application_amendment_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_amendment_notification.txt'

class ApplicationAssessmentRequestedEmail(TemplateEmailBase):
    subject = 'Wildlife licensing assessment required'
    html_template = 'wildlifecompliance/emails/send_application_assessment_request_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_assessment_request_notification.txt'

class ApplicationAssessmentReminderEmail(TemplateEmailBase):
    subject = 'Wildlife licensing assessment reminder'
    html_template = 'wildlifecompliance/emails/send_application_assessment_remind_notification.html'
    txt_template = 'wildlifecompliance/emails/send_application_assessment_remind_notification.txt'


def send_assessment_reminder_email(assessment, request=None):
    application = assessment.application

    email = ApplicationAssessmentReminderEmail()
    url = request.build_absolute_uri(reverse('internal-application-detail',kwargs={'application_pk': application.id}))
    context = {
        'url': url
    }
    msg = email.send(select_group, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)



    
def send_assessment_email_notification(select_group,assessment, request):
    email_group=[]
    application = assessment.application
    email = ApplicationAssessmentRequestedEmail()
    url = request.build_absolute_uri(reverse('internal-application-detail',kwargs={'application_pk': application.id}))
    context = {
        'url': url
    }
   
    email_group=[item.email for item in select_group]
    msg = email.send(email_group, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)




def send_referral_email_notification(emails,application,request,reminder=False):
    email = ReferralSendNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-referral-detail',kwargs={'application_pk':referral.application.id,'referral_pk':referral.id}))

    context = {
        'application': application
    }

    msg = email.send(emails, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, referral, sender=sender)
    _log_org_email(msg, referral.application.applicant, referral.referral, sender=sender)


def send_application_submit_email_notification(group_email,application,request):
    # An email to internal users notifying about new application is submitted
    email = ApplicationSubmitNotificationEmail()
    # url = request.build_absolute_uri(reverse('internal-application-detail',kwargs={'application_pk':referral.application.id,'referral_pk':referral.id}))
    url = request.build_absolute_uri(reverse('internal-application-detail',kwargs={'application_pk': application.id}))

    context = {
        'application': application,
        'url': url
    }

    msg = email.send(group_email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    # _log_application_email(msg, referral, sender=sender)
    # _log_org_email(msg, referral.application.applicant, referral.referral, sender=sender)

def send_application_amendment_notification(amendment,application,request):
    # An email to internal users notifying about new application is submitted
    email = ApplicationAmendmentRequestNotificationEmail()
    reason = amendment.get_reason_display()
    url = request.build_absolute_uri(reverse('external-application-detail',kwargs={'application_pk': application.id}))
    context = {
        'application': application,
        'reason': reason,
        'amendment_details': amendment.text,
        'url': url
    }

    msg = email.send(application.submitter.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_application_email(msg, application, sender=sender)


def _log_application_email(email_message, application, sender=None):
    from wildlifecompliance.components.applications.models import ApplicationLogEntry
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
        to = application.submitter.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = application.submitter

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'application': application,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = ApplicationLogEntry.objects.create(**kwargs)

    return email_entry

def _log_org_email(email_message, organisation, customer ,sender=None):
    from wildlifecompliance.components.organisations.models import OrganisationLogEntry
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
