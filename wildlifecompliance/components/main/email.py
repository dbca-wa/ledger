import logging
import traceback
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings
from ledger.payments.pdf import create_invoice_pdf_bytes
from ledger.payments.models import Invoice
from wildlifecompliance.components.main.utils import get_choice_value
from wildlifecompliance.components.emails.emails import TemplateEmailBase
from wildlifecompliance.components.users.models import CompliancePermissionGroup
from ledger.accounts.models import EmailUser
import os

logger = logging.getLogger(__name__)

SYSTEM_NAME = 'Wildlife Licensing Automated Message'


def prepare_attachments(attachments):
    returned_attachments = []
    for document in attachments.all():
        path, filename = os.path.split(document._file.name)    
        returned_attachments.append(
            (filename, document._file.read())
        )
    return returned_attachments

def _extract_email_headers(email_message, sender=None):
    print(sender)
    if isinstance(email_message, (EmailMultiAlternatives, EmailMessage,)):
        # TODO this will log the plain text body, should we log the html
        # instead
        text = email_message.body
        subject = email_message.subject
        fromm = smart_text(sender) if sender else smart_text(
            email_message.from_email)
        # the to email is normally a list
        if isinstance(email_message.to, list):
            to = ','.join(email_message.to)
        else:
            to = smart_text(email_message.to)
        # we log the cc and bcc in the same cc field of the log entry as a ','
        # comma separated string
        all_ccs = []
        if email_message.cc:
            all_ccs += list(email_message.cc)
        if email_message.bcc:
            all_ccs += list(email_message.bcc)
        all_ccs = ','.join(all_ccs)

    else:
        text = smart_text(email_message)
        subject = ''
        to = ''
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    email_data = {
        'subject': subject,
        'text': text,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    return email_data

# Each component will implement a send_mail method to pass to this function.
# Eg. SanctionOutcome will have send_sanction_outcome_email api method
def prepare_mail(request, instance, workflow_entry, send_mail, recipient_id=None):
    try:
        email_group = []
        if recipient_id:
            user = EmailUser.objects.get(id=recipient_id)
            email_group.append(user)
        elif request.data.get('assigned_to_id'):
            user = EmailUser.objects.get(id=request.data.get('assigned_to_id'))
            email_group.append(user)
        elif request.data.get('allocated_group_id'):
            compliance_group = CompliancePermissionGroup.objects.get(id=request.data.get('allocated_group_id'))
            email_group.extend(compliance_group.members.all())
        else:
            email_group.append(request.user)

        print("email_group")
        print(email_group)

        # send email
        email_data = send_mail(
            email_group,
            instance,
            workflow_entry,
            request)

        return email_data

    except Exception as e:
        print(traceback.print_exc())

