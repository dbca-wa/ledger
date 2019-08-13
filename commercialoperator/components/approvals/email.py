import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings

from commercialoperator.components.emails.emails import TemplateEmailBase
from ledger.accounts.models import EmailUser

logger = logging.getLogger(__name__)

SYSTEM_NAME = settings.SYSTEM_NAME_SHORT + ' Automated Message'
class ApprovalExpireNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval has been expired.'
    html_template = 'commercialoperator/emails/approval_expire_notification.html'
    txt_template = 'commercialoperator/emails/approval_expire_notification.txt'


class ApprovalCancelNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval has been cancelled.'
    html_template = 'commercialoperator/emails/approval_cancel_notification.html'
    txt_template = 'commercialoperator/emails/approval_cancel_notification.txt'

class ApprovalSuspendNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval has been suspended.'
    html_template = 'commercialoperator/emails/approval_suspend_notification.html'
    txt_template = 'commercialoperator/emails/approval_suspend_notification.txt'

class ApprovalSurrenderNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval has been surrendered.'
    html_template = 'commercialoperator/emails/approval_surrender_notification.html'
    txt_template = 'commercialoperator/emails/approval_surrender_notification.txt'

class ApprovalReinstateNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval has been reinstated.'
    html_template = 'commercialoperator/emails/approval_reinstate_notification.html'
    txt_template = 'commercialoperator/emails/approval_reinstate_notification.txt'

class ApprovalRenewalNotificationEmail(TemplateEmailBase):
    subject = 'Your Approval is due for renewal.'
    html_template = 'commercialoperator/emails/approval_renewal_notification.html'
    txt_template = 'commercialoperator/emails/approval_renewal_notification.txt'

def send_approval_expire_email_notification(approval):
    email = ApprovalExpireNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'proposal': proposal
    }
    msg = email.send(proposal.submitter.email, context=context)
    sender = settings.DEFAULT_FROM_EMAIL
    try:
    	sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        EmailUser.objects.create(email=sender, password='')
        sender_user = EmailUser.objects.get(email__icontains=sender)
    _log_approval_email(msg, approval, sender=sender_user)
    #_log_org_email(msg, approval.applicant, proposal.submitter, sender=sender_user)
    if approval.org_applicant:
        _log_org_email(msg, approval.org_applicant, proposal.submitter, sender=sender_user)
    else:
        _log_user_email(msg, approval.submitter, proposal.submitter, sender=sender_user)

def send_approval_cancel_email_notification(approval):
    email = ApprovalCancelNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,

    }
    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        EmailUser.objects.create(email=sender, password='')
        sender_user = EmailUser.objects.get(email__icontains=sender)
    msg = email.send(proposal.submitter.email, context=context)
    sender = settings.DEFAULT_FROM_EMAIL
    _log_approval_email(msg, approval, sender=sender_user)
    #_log_org_email(msg, approval.applicant, proposal.submitter, sender=sender_user)
    if approval.org_applicant:
        _log_org_email(msg, approval.org_applicant, proposal.submitter, sender=sender_user)
    else:
        _log_user_email(msg, approval.submitter, proposal.submitter, sender=sender_user)

def send_approval_suspend_email_notification(approval):
    email = ApprovalSuspendNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'details': approval.suspension_details['details'],
        'from_date': approval.suspension_details['from_date'],
        'to_date': approval.suspension_details['to_date']
    }
    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        EmailUser.objects.create(email=sender, password='')
        sender_user = EmailUser.objects.get(email__icontains=sender)
    msg = email.send(proposal.submitter.email, context=context)
    sender = settings.DEFAULT_FROM_EMAIL
    _log_approval_email(msg, approval, sender=sender_user)
    #_log_org_email(msg, approval.applicant, proposal.submitter, sender=sender_user)
    if approval.org_applicant:
        _log_org_email(msg, approval.org_applicant, proposal.submitter, sender=sender_user)
    else:
        _log_user_email(msg, approval.submitter, proposal.submitter, sender=sender_user)

def send_approval_surrender_email_notification(approval):
    email = ApprovalSurrenderNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'details': approval.surrender_details['details'],
        'surrender_date': approval.surrender_details['surrender_date'],
    }
    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        EmailUser.objects.create(email=sender, password='')
        sender_user = EmailUser.objects.get(email__icontains=sender)
    msg = email.send(proposal.submitter.email, context=context)
    sender = settings.DEFAULT_FROM_EMAIL
    _log_approval_email(msg, approval, sender=sender_user)
    if approval.org_applicant:
        _log_org_email(msg, approval.org_applicant, proposal.submitter, sender=sender_user)
    else:
        _log_user_email(msg, approval.submitter, proposal.submitter, sender=sender_user)
#approval renewal notice
def send_approval_renewal_email_notification(approval):
    email = ApprovalRenewalNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,
        'proposal': approval.current_proposal

    }
    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        EmailUser.objects.create(email=sender, password='')
        sender_user = EmailUser.objects.get(email__icontains=sender)
    #attach renewal notice
    renewal_document= approval.renewal_document._file
    if renewal_document is not None:
        file_name = approval.renewal_document.name
        attachment = (file_name, renewal_document.file.read(), 'application/pdf')
        attachment = [attachment]
    else:
        attachment = []
    msg = email.send(proposal.submitter.email, attachments=attachment, context=context)
    sender = settings.DEFAULT_FROM_EMAIL
    _log_approval_email(msg, approval, sender=sender_user)
    #_log_org_email(msg, approval.applicant, proposal.submitter, sender=sender_user)
    if approval.org_applicant:
        _log_org_email(msg, approval.org_applicant, proposal.submitter, sender=sender_user)
    else:
        _log_user_email(msg, approval.submitter, proposal.submitter, sender=sender_user)


def send_approval_reinstate_email_notification(approval, request):
    email = ApprovalReinstateNotificationEmail()
    proposal = approval.current_proposal

    context = {
        'approval': approval,

    }
    msg = email.send(proposal.submitter.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_approval_email(msg, approval, sender=sender)
    #_log_org_email(msg, approval.applicant, proposal.submitter, sender=sender)
    if approval.org_applicant:
        _log_org_email(msg, approval.org_applicant, proposal.submitter, sender=sender_user)
    else:
        _log_user_email(msg, approval.submitter, proposal.submitter, sender=sender_user)



def _log_approval_email(email_message, approval, sender=None):
    from commercialoperator.components.approvals.models import ApprovalLogEntry
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
        to = approval.current_proposal.submitter.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = approval.current_proposal.submitter

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'approval': approval,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = ApprovalLogEntry.objects.create(**kwargs)

    return email_entry




from commercialoperator.components.organisations.models import OrganisationLogEntry, Organisation
def _log_org_email(email_message, organisation, customer ,sender=None):
    if not isinstance(organisation, Organisation):
        # is a proxy_applicant
        return None

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
        to = customer
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

def _log_user_email(email_message, emailuser, customer ,sender=None):
    from ledger.accounts.models import EmailUserLogEntry
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
        to = customer
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = customer

    staff = sender
    #import ipdb; ipdb.set_trace()

    kwargs = {
        'subject': subject,
        'text': text,
        'emailuser': emailuser,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = EmailUserLogEntry.objects.create(**kwargs)

    return email_entry

