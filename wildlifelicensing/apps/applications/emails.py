import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.encoding import smart_text

from wildlifelicensing.apps.emails.emails import TemplateEmailBase, host_reverse, pdf_host_reverse
from wildlifelicensing.apps.applications.models import ApplicationLogEntry, IDRequest, ReturnsRequest, AmendmentRequest

SYSTEM_NAME = 'Wildlife Licensing Automated Message'
MAX_SUBJECT_LENGTH = 76

logger = logging.getLogger(__name__)


def _format_application_email_subject(subject, application):
    subject = subject.format(application.reference, application.applicant.get_full_name())

    # subject can be no longer than MAX_SUBJECT_LENGTH
    if len(subject) > MAX_SUBJECT_LENGTH:
        subject = '{}..'.format(subject[:MAX_SUBJECT_LENGTH - 2])

    return subject


class ApplicationAmendmentRequestedEmail(TemplateEmailBase):
    subject = 'An amendment to your wildlife licensing application is required.'
    html_template = 'wl/emails/application_amendment_requested.html'
    txt_template = 'wl/emails/application_amendment_requested.txt'


def send_amendment_requested_email(amendment_request, request):
    application = amendment_request.application
    email = ApplicationAmendmentRequestedEmail()
    url = pdf_host_reverse('wl_applications:edit_application', args=[application.pk])

    context = {
        'amendment_request': amendment_request,
        'url': url
    }

    if amendment_request.reason:
        context['reason'] = dict(AmendmentRequest.REASON_CHOICES)[amendment_request.reason]

    if application.proxy_applicant is None:
        recipient_email = application.applicant_profile.email
    else:
        recipient_email = application.proxy_applicant.email

    msg = email.send(recipient_email, context=context)
    _log_email(msg, application=application, sender=request.user)


class ApplicationAssessmentRequestedEmail(TemplateEmailBase):
    subject = 'Wildlife licensing [{} {}]: assessment required'
    html_template = 'wl/emails/application_assessment_requested.html'
    txt_template = 'wl/emails/application_assessment_requested.txt'

    def __init__(self, application):
        self.subject = _format_application_email_subject(self.subject, application)


def send_assessment_requested_email(assessment, request):
    application = assessment.application

    email = ApplicationAssessmentRequestedEmail(application)
    url = request.build_absolute_uri(
        reverse('wl_applications:enter_conditions_assessor',
                args=[application.pk, assessment.pk])
    )
    context = {
        'url': url
    }
    msg = email.send(assessment.assessor_group.email, context=context)

    _log_email(msg, application=application, sender=request.user)


class ApplicationAssessmentAssignedEmail(TemplateEmailBase):
    subject = 'Wildlife licensing [{} {}]: assessment assigned.'
    html_template = 'wl/emails/application_assessment_assigned.html'
    txt_template = 'wl/emails/application_assessment_assigned.txt'

    def __init__(self, application):
        self.subject = _format_application_email_subject(self.subject, application)


def send_assessment_assigned_email(assessment, request):
    application = assessment.application
    assigned_assessor = assessment.assigned_assessor
    if assigned_assessor is not None and assigned_assessor.email:
        recipient = assigned_assessor.email
        email = ApplicationAssessmentAssignedEmail(application)
        url = request.build_absolute_uri(
            reverse('wl_applications:enter_conditions_assessor',
                    args=[application.pk, assessment.pk])
        )
        context = {
            'url': url
        }
        msg = email.send(recipient, context=context)

        _log_email(msg, application=application, sender=request.user)


class ApplicationAssessmentReminderEmail(TemplateEmailBase):
    subject = 'Wildlife licensing [{} {}]: Reminder - assessment required'
    html_template = 'wl/emails/application_assessment_reminder.html'
    txt_template = 'wl/emails/application_assessment_reminder.txt'

    def __init__(self, application):
        self.subject = _format_application_email_subject(self.subject, application)


def send_assessment_reminder_email(assessment, request=None):
    application = assessment.application

    email = ApplicationAssessmentReminderEmail(application)
    if request is not None:
        url = request.build_absolute_uri(
            reverse('wl_applications:enter_conditions_assessor',
                    args=(application.pk, assessment.pk))
        )
    else:
        url = host_reverse('wl_applications:enter_conditions_assessor', args=(application.pk, assessment.pk))

    context = {
        'assessor': assessment.assessor_group,
        'url': url
    }

    msg = email.send(assessment.assessor_group.email, context=context)
    sender = request.user if request is not None else None
    _log_email(msg, application=application, sender=sender)


class ApplicationAssessmentDoneEmail(TemplateEmailBase):
    subject = 'Wildlife licensing [{} {}]: assessment complete'
    html_template = 'wl/emails/application_assessment_done.html'
    txt_template = 'wl/emails/application_assessment_done.txt'

    def __init__(self, application):
        self.subject = _format_application_email_subject(self.subject, application)


def send_assessment_done_email(assessment, request):
    application = assessment.application

    email = ApplicationAssessmentDoneEmail(application)
    url = request.build_absolute_uri(
        reverse('wl_applications:enter_conditions',
                args=[application.pk])
    )
    context = {
        'assessor': request.user,
        'assessor_group': assessment.assessor_group,
        'url': url
    }
    to_email = application.assigned_officer.email if application.assigned_officer else \
        settings.EMAIL_FROM
    msg = email.send(to_email, context=context)
    _log_email(msg, application=application, sender=request.user)


class ApplicationIDUpdateRequestedEmail(TemplateEmailBase):
    subject = 'An ID update for a wildlife licensing application is required.'
    html_template = 'wl/emails/application_id_request.html'
    txt_template = 'wl/emails/application_id_request.txt'


def send_id_update_request_email(id_request, request):
    application = id_request.application
    email = ApplicationIDUpdateRequestedEmail()
    url = pdf_host_reverse('wl_main:identification')

    if id_request.reason:
        id_request.reason = dict(IDRequest.REASON_CHOICES)[id_request.reason]

    context = {
        'id_request': id_request,
        'url': url
    }

    if application.proxy_applicant is None:
        recipient_email = application.applicant_profile.email
    else:
        recipient_email = application.proxy_applicant.email

    msg = email.send(recipient_email, context=context)
    _log_email(msg, application=application, sender=request.user)


class ApplicationReturnsRequestedEmail(TemplateEmailBase):
    subject = 'Completion of returns for a wildlife licensing application is required.'
    html_template = 'wl/emails/application_returns_request.html'
    txt_template = 'wl/emails/application_returns_request.txt'


def send_returns_request_email(returns_request, request):
    application = returns_request.application
    email = ApplicationReturnsRequestedEmail()
    url = pdf_host_reverse('wl_dashboard:home')

    if returns_request.reason:
        returns_request.reason = dict(ReturnsRequest.REASON_CHOICES)[returns_request.reason]

    context = {
        'url': url,
        'returns_request': returns_request
    }

    if application.proxy_applicant is None:
        recipient_email = application.applicant_profile.email
    else:
        recipient_email = application.proxy_applicant.email

    msg = email.send(recipient_email, context=context)
    _log_email(msg, application=application, sender=request.user)


class LicenceIssuedEmail(TemplateEmailBase):
    subject = 'Your wildlife licensing licence has been issued.'
    html_template = 'wl/emails/licence_issued.html'
    txt_template = 'wl/emails/licence_issued.txt'


def send_licence_issued_email(licence, application, request, to=None, cc=None, bcc=None, additional_attachments=None):
    email = LicenceIssuedEmail()
    url = request.build_absolute_uri(
        reverse('wl_dashboard:home')
    )
    context = {
        'url': url,
        'licence': licence
    }
    if licence.licence_document is not None:
        file_name = 'WL_licence_' + smart_text(licence.licence_type.product_title)
        if licence.licence_number:
            file_name += '_' + smart_text(licence.licence_number)
        if licence.licence_sequence:
            file_name += '-' + smart_text(licence.licence_sequence)
        elif licence.start_date:
            file_name += '_' + smart_text(licence.start_date)
        file_name += '.pdf'
        attachment = (file_name, licence.licence_document.file.read(), 'application/pdf')
        attachments = [attachment]
    else:
        logger.error('The licence pk=' + licence.pk + ' has no document associated with it.')
        attachments = []
    if not to:
        to = [licence.profile.email]
    if additional_attachments and not isinstance(additional_attachments, list):
        additional_attachments = list(additional_attachments)

    other_attachments = []
    pdf_attachments = []
    if additional_attachments:
        for a in additional_attachments:
            if a.file.name.endswith('.pdf'):
                pdf_attachments.append(a)
            else:
                other_attachments.append(a)
        attachments += other_attachments
    msg = email.send(to, context=context, attachments=attachments, cc=cc, bcc=bcc)
    log_entry = _log_email(msg, application=application, sender=request.user)
    if licence.licence_document is not None:
        log_entry.documents.add(licence.licence_document)
    if additional_attachments:
        log_entry.documents.add(*other_attachments)
    return log_entry


class UserNameChangeNotificationEmail(TemplateEmailBase):
    subject = 'User has changed name and requires licence reissue.'
    html_template = 'wl/emails/user_name_change_notification.html'
    txt_template = 'wl/emails/user_name_change_notification.txt'


def send_user_name_change_notification_email(licence):
    email = UserNameChangeNotificationEmail()

    url = host_reverse('wl_applications:reissue_licence', args=(licence.pk,))

    context = {
        'licence': licence,
        'url': url
    }
    email.send(licence.issuer.email, context=context)


class ApplicationDeclinedEmail(TemplateEmailBase):
    subject = 'Wildlife licensing [{} {}]: application declined'
    html_template = 'wl/emails/application_declined.html'
    txt_template = 'wl/emails/application_declined.txt'

    def __init__(self, application):
        self.subject = _format_application_email_subject(self.subject, application)


def send_application_declined_email(declined_details, request):
    application = declined_details.application
    email = ApplicationDeclinedEmail(application)
    url = request.build_absolute_uri(reverse('wl_home')) if request else None

    reason_text = declined_details.reason or ''
    reason_html = reason_text.replace('\n', '<br/>')

    context = {
        'reason_text': reason_text,
        'reason_html': reason_html,
        'wl_home': url
    }

    if application.proxy_applicant is None:
        recipient_email = application.applicant_profile.email
    else:
        recipient_email = application.proxy_applicant.email

    msg = email.send(recipient_email, context=context)
    sender = request.user if request else settings.EMAIL_FROM
    _log_email(msg, application=application, sender=sender)
    return recipient_email


def _log_email(email_message, application, sender=None):
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
        to = application.applicant.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = application.applicant

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
