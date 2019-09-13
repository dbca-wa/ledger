import logging
import traceback

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings

from ledger.accounts.models import EmailUser
from ledger.payments.pdf import create_invoice_pdf_bytes
from ledger.payments.models import Invoice
from wildlifecompliance.components.main.utils import get_choice_value
from wildlifecompliance.components.emails.emails import TemplateEmailBase
from wildlifecompliance.components.main.email import prepare_attachments, _extract_email_headers
import os

from wildlifecompliance.components.users.models import CompliancePermissionGroup

logger = logging.getLogger(__name__)

SYSTEM_NAME = 'Wildlife Licensing Automated Message'


class SanctionOutcomeIssueNotificationEmail(TemplateEmailBase):
    subject = 'Issued Sanction Outcome'
    html_template = 'wildlifecompliance/emails/issue_sanction_outcome_notification.html'
    txt_template = 'wildlifecompliance/emails/issue_sanction_outcome_notification.txt'


def send_mail(select_group, sanction_outcome, workflow_entry, request=None):
    email = SanctionOutcomeIssueNotificationEmail()
    if request.data.get('email_subject'):
        email.subject = request.data.get('email_subject')
    url = request.build_absolute_uri(
        reverse(
            'internal-sanction-outcome-detail',
            kwargs={
                'sanction_outcome_id': sanction_outcome.id
                }))
    context = {
        'url': url,
        'sanction_outcome': sanction_outcome,
        'workflow_entry_details': request.data.get('details'),
    }
    email_group = [item.email for item in select_group]
    msg = email.send(email_group, 
        context=context,
        attachments= 
        prepare_attachments(workflow_entry.documents)
        )
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    email_data = _extract_email_headers(msg, sender=sender)
    return email_data

def get_email_recipients(sanction_outcome, recipient_id=None, recipient_final=None):
    try:
        email_group = []

        if recipient_id:
            user = EmailUser.objects.get(id=recipient_id)
            email_group.append(user)
        elif sanction_outcome.assigned_to_id:
            user = EmailUser.objects.get(id=sanction_outcome.assigned_to_id)
            email_group.append(user)
        elif sanction_outcome.allocated_group_id:
            compliance_group = CompliancePermissionGroup.objects.get(id=sanction_outcome.allocated_group_id)
            email_group.extend(compliance_group.members.all())
        else:
            if recipient_final:
                email_group.append(recipient_final)

        return email_group

    except Exception as e:
        print(traceback.print_exc())

