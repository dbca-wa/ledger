from django.core.mail import EmailMultiAlternatives, EmailMessage

from wildlifelicensing.apps.emails.emails import TemplateEmailBase
from wildlifelicensing.apps.applications.models import EmailLogEntry


class ApplicationAmendmentRequestedEmail(TemplateEmailBase):
    subject = 'An amendment to you wildlife licensing application is required.'
    html_template = 'wl/emails/application_amendment_requested.html'
    # txt_template can be None, in this case a 'tag-stripped' version of the html will be sent. (see send)
    txt_template = 'wl/emails/application_amendment_requested.txt'


def send_amendment_requested_email(application, amendment_request, request):
    email = ApplicationAmendmentRequestedEmail()
    context = {
        'amendment': amendment_request.text
    }

    msg = email.send(application.applicant_persona.email, context=context)
    _log_email(msg, application=application, sender=request.user)


def _log_email(email_message, application, sender=None):
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        email_message = email_message.body
    kwargs = {
        'text': str(email_message),
        'application': application,
        'user': sender
    }
    email_entry = EmailLogEntry.objects.create(**kwargs)
    return email_entry
