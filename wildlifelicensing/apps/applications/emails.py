import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.encoding import smart_text

from django_hosts import reverse as hosts_reverse

from wildlifelicensing.apps.emails.emails import TemplateEmailBase
from wildlifelicensing.apps.applications.models import EmailLogEntry, AmendmentRequest, IDRequest

logger = logging.getLogger(__name__)


class ApplicationAmendmentRequestedEmail(TemplateEmailBase):
    subject = 'An amendment to your wildlife licensing application is required.'
    html_template = 'wl/emails/application_amendment_requested.html'
    txt_template = 'wl/emails/application_amendment_requested.txt'


class ApplicationAssessmentReminderEmail(TemplateEmailBase):
    subject = 'Reminder: An amendment to you wildlife licensing application is required.'
    html_template = 'wl/emails/application_assessment_reminder.html'
    txt_template = 'wl/emails/application_assessment_reminder.txt'


def send_amendment_requested_email(application, amendment_request, request):
    email = ApplicationAmendmentRequestedEmail()
    url = request.build_absolute_uri(
        reverse('wl_applications:edit_application',
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
        reverse('wl_applications:enter_conditions_assessor',
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
        reverse('wl_applications:enter_conditions_assessor',
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
        reverse('wl_applications:enter_conditions',
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
        reverse('wl_main:identification')
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


class LicenceIssuedEmail(TemplateEmailBase):
    subject = 'Your wildlife licensing licence has been issued.'
    html_template = 'wl/emails/licence_issued.html'
    txt_template = 'wl/emails/licence_issued.txt'


def send_licence_issued_email(licence, application, cover_letter_message, request):
    email = LicenceIssuedEmail()
    url = request.build_absolute_uri(
        reverse('wl_dashboard:home')
    )
    context = {
        'url': url,
        'cover_letter_message': cover_letter_message
    }
    if licence.document is not None:
        file_name = 'WL_licence_' + smart_text(licence.licence_type.code)
        if licence.licence_no:
            file_name += '_' + smart_text(licence.licence_no)
        elif licence.start_date:
            file_name += '_' + smart_text(licence.start_date)
        file_name += '.pdf'
        attachment = (file_name, licence.document.file.read(), 'application/pdf')
        attachments = [attachment]
    else:
        logger.error('The licence pk=' + licence.pk + ' has no document associated with it.')
        attachments = None
    msg = email.send(licence.profile.email, context=context, attachments=attachments)
    log_entry = _log_email(msg, application=application, sender=request.user)
    if licence.document is not None:
        log_entry.document = licence.document
        log_entry.save()
    return log_entry


class LicenceRenewalNotificationEmail(TemplateEmailBase):
    subject = 'Your wildlife licence is due for renewal.'
    html_template = 'wl/emails/renew_licence_notification.html'
    txt_template = 'wl/emails/renew_licence_notification.txt'


def send_licence_renewal_email_notification(licence):
    email = LicenceRenewalNotificationEmail()
    url = 'http:' + hosts_reverse('wl_applications:renew_licence', args=(licence.pk,))

    context = {
        'url': url,
        'licence': licence
    }

    email.send(licence.profile.email, context=context)


def _log_email(email_message, application, sender=None):
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html instead
        text = email_message.body
        subject = email_message.subject
        from_email = smart_text(sender) if sender else smart_text(email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ';'.join(email_message.to)
        else:
            to = smart_text(email_message.to)
    else:
        text = smart_text(email_message)
        subject = ''
        to = application.applicant_profile.user.email
        from_email = smart_text(sender) if sender else ''

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
