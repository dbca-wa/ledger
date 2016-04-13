from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.urlresolvers import reverse

from wildlifelicensing.apps.emails.emails import TemplateEmailBase
from wildlifelicensing.apps.applications.models import EmailLogEntry


class ApplicationAmendmentRequestedEmail(TemplateEmailBase):
    subject = 'An amendment to you wildlife licensing application is required.'
    html_template = 'wl/emails/application_amendment_requested.html'
    txt_template = 'wl/emails/application_amendment_requested.txt'


def send_amendment_requested_email(application, amendment_request, request):
    email = ApplicationAmendmentRequestedEmail()
    url = request.build_absolute_uri(
        reverse('applications:enter_details_existing_application',
                args=[application.licence_type.code, application.pk])
    )
    context = {
        'amendment': amendment_request.text,
        'url': url
    }
    msg = email.send(application.applicant_profile.email, context=context)
    _log_email(msg, application=application, sender=request.user)


class ApplicationAssessmentRequestedEmail(TemplateEmailBase):
    subject = 'An assessment to a wildlife licensing application is required.'
    html_template = 'wl/emails/application_assessment_requested.html'
    txt_template = 'wl/emails/application_assessment_requested.txt'


def send_assessment_requested_email(application, assessment_request, request):
    email = ApplicationAssessmentRequestedEmail()
    url = request.build_absolute_uri(
        reverse('applications:process',
                args=[application.pk])
    )
    context = {
        'assessor': assessment_request.assessor,
        'url': url
    }
    msg = email.send(application.applicant_profile.email, context=context)
    _log_email(msg, application=application, sender=request.user)


def _log_email(email_message, application, sender=None):
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html instead
        # TODO log the subject of the email
        email_message = email_message.body
    kwargs = {
        'text': str(email_message),
        'application': application,
        'user': sender
    }
    email_entry = EmailLogEntry.objects.create(**kwargs)
    return email_entry
