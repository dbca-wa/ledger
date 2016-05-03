from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.urlresolvers import reverse
from django.conf import settings

from wildlifelicensing.apps.emails.emails import TemplateEmailBase
from wildlifelicensing.apps.applications.models import EmailLogEntry, AmendmentRequest, IDRequest


class ApplicationAmendmentRequestedEmail(TemplateEmailBase):
    subject = 'An amendment to your wildlife licensing application is required.'
    html_template = 'wl/emails/application_amendment_requested.html'
    txt_template = 'wl/emails/application_amendment_requested.txt'


class ApplicationAssessmentReminderEmail(TemplateEmailBase):
    subject = 'Reminder: An amendment to you wildlife licensing application is required.'
    html_template = 'wl/emails/application_amendment_reminder.html'
    txt_template = 'wl/emails/application_amendment_reminder.txt'


def send_amendment_requested_email(application, amendment_request, request):
    email = ApplicationAmendmentRequestedEmail()
    url = request.build_absolute_uri(
        reverse('applications:edit_application',
                args=[application.licence_type.code, application.pk])
    )
    context = {
        'amendment_detail': amendment_request.text,
        'url': url
    }
    if amendment_request.reason:
        context['amendment_reason'] = dict(AmendmentRequest.REASON_CHOICES)[amendment_request.reason]
    msg = email.send(application.applicant_profile.email, context=context)
    _log_email(msg, application=application, sender=request.user)


class ApplicationAssessmentRequestedEmail(TemplateEmailBase):
    subject = 'An assessment to a wildlife licensing application is required.'
    html_template = 'wl/emails/application_assessment_requested.html'
    txt_template = 'wl/emails/application_assessment_requested.txt'


def send_assessment_requested_email(assessment, request):
    application = assessment.application

    email = ApplicationAssessmentRequestedEmail()
    url = request.build_absolute_uri(
        reverse('applications:enter_conditions_assessor',
                args=[application.pk, assessment.pk])
    )
    context = {
        'assessor': assessment.assessor_group,
        'url': url
    }
    msg = email.send(assessment.assessor_group.email, context=context)
    _log_email(msg, application=application, sender=request.user)


def send_assessment_reminder_email(assessment, request):
    application = assessment.application

    email = ApplicationAssessmentReminderEmail()
    url = request.build_absolute_uri(
        reverse('applications:enter_conditions_assessor',
                args=[application.pk, assessment.pk])
    )
    context = {
        'assessor': assessment.assessor_group,
        'url': url
    }
    msg = email.send(assessment.assessor_group.email, context=context)
    _log_email(msg, application=application, sender=request.user)


class ApplicationAssessmentDoneEmail(TemplateEmailBase):
    subject = 'An assessment to a wildlife licensing application has been done.'
    html_template = 'wl/emails/application_assessment_done.html'
    txt_template = 'wl/emails/application_assessment_done.txt'


def send_assessment_done_email(assessment, request):
    application = assessment.application

    email = ApplicationAssessmentDoneEmail()
    url = request.build_absolute_uri(
        reverse('applications:enter_conditions',
                args=[application.pk])
    )
    context = {
        'assessor': request.user,
        'assessor_group': assessment.assessor_group,
        'url': url
    }
    to_email = application.assigned_officer.email if application.assigned_officer else settings.WILDLIFELICENSING_EMAIL_CATCHALL
    msg = email.send(to_email, context=context)
    _log_email(msg, application=application, sender=request.user)


class ApplicationIDUpdateRequestedEmail(TemplateEmailBase):
    subject = 'An ID update for a wildlife licensing application is required.'
    html_template = 'wl/emails/application_id_request.html'
    txt_template = 'wl/emails/application_id_request.txt'


def send_id_update_request_email(id_request, request):
    email = ApplicationIDUpdateRequestedEmail()
    url = request.build_absolute_uri(
        reverse('main:identification')
    )
    context = {
        'url': url
    }
    if id_request.reason:
        context['request_reason'] = dict(IDRequest.REASON_CHOICES)[id_request.reason]
    if id_request.text:
        context['request_text'] = id_request.text
    msg = email.send(id_request.application.applicant_profile.email, context=context)
    _log_email(msg, application=id_request.application, sender=request.user)


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
