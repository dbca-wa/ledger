import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings

from disturbance.components.emails.emails import TemplateEmailBase
from ledger.accounts.models import EmailUser

logger = logging.getLogger(__name__)

SYSTEM_NAME = settings.SYSTEM_NAME_SHORT + ' Automated Message'
class ReferralSendNotificationEmail(TemplateEmailBase):
    subject = 'A referral for a proposal has been sent to you.'
    html_template = 'disturbance/emails/proposals/send_referral_notification.html'
    txt_template = 'disturbance/emails/proposals/send_referral_notification.txt'

class ReferralCompleteNotificationEmail(TemplateEmailBase):
    subject = 'A referral for a proposal has been completed.'
    html_template = 'disturbance/emails/proposals/send_referral_complete_notification.html'
    txt_template = 'disturbance/emails/proposals/send_referral_complete_notification.txt'

class ReferralRecallNotificationEmail(TemplateEmailBase):
    subject = 'A referral for a proposal has been recalled.'
    html_template = 'disturbance/emails/proposals/send_referral_recall_notification.html'
    txt_template = 'disturbance/emails/proposals/send_referral_recall_notification.txt'    

class ProposalDeclineSendNotificationEmail(TemplateEmailBase):
    subject = 'Your Proposal has been declined.'
    html_template = 'disturbance/emails/proposals/send_decline_notification.html'
    txt_template = 'disturbance/emails/proposals/send_decline_notification.txt'

class ProposalApprovalSendNotificationEmail(TemplateEmailBase):
    subject = 'Your Proposal has been approved.'
    html_template = 'disturbance/emails/proposals/send_approval_notification.html'
    txt_template = 'disturbance/emails/proposals/send_approval_notification.txt'

class AmendmentRequestSendNotificationEmail(TemplateEmailBase):
    subject = 'An amendment to your Proposal is required.'
    html_template = 'disturbance/emails/proposals/send_amendment_notification.html'
    txt_template = 'disturbance/emails/proposals/send_amendment_notification.txt'

class SubmitSendNotificationEmail(TemplateEmailBase):
    subject = 'A new Proposal has been submitted.'
    html_template = 'disturbance/emails/proposals/send_submit_notification.html'
    txt_template = 'disturbance/emails/proposals/send_submit_notification.txt'

class AssessmentReminderSendNotificationEmail(TemplateEmailBase):
    subject = 'A Proposal is waiting for assessment.'
    html_template = 'disturbance/emails/proposals/send_assessment_reminder_notification.html'
    txt_template = 'disturbance/emails/proposals/send_assessment_reminder_notification.txt'

class ExternalSubmitSendNotificationEmail(TemplateEmailBase):
    subject = 'A new Proposal has been submitted.'
    html_template = 'disturbance/emails/proposals/send_external_submit_notification.html'
    txt_template = 'disturbance/emails/proposals/send_external_submit_notification.txt'

class ApproverDeclineSendNotificationEmail(TemplateEmailBase):
    subject = 'A Proposal has been recommended for decline.'
    html_template = 'disturbance/emails/proposals/send_approver_decline_notification.html'
    txt_template = 'disturbance/emails/proposals/send_approver_decline_notification.txt'

class ApproverApproveSendNotificationEmail(TemplateEmailBase):
    subject = 'A Proposal has been recommended for approval.'
    html_template = 'disturbance/emails/proposals/send_approver_approve_notification.html'
    txt_template = 'disturbance/emails/proposals/send_approver_approve_notification.txt'

class ApproverSendBackNotificationEmail(TemplateEmailBase):
    subject = 'A Proposal has been sent back by approver.'
    html_template = 'disturbance/emails/proposals/send_approver_sendback_notification.html'
    txt_template = 'disturbance/emails/proposals/send_approver_sendback_notification.txt'

def send_referral_email_notification(referral,request,reminder=False):
    email = ReferralSendNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-referral-detail',kwargs={'proposal_pk':referral.proposal.id,'referral_pk':referral.id}))

    context = {
        'proposal': referral.proposal,
        'url': url,
        'reminder':reminder,
        'comments': referral.text
    }

    msg = email.send(referral.referral.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_referral_email(msg, referral, sender=sender)
    _log_org_email(msg, referral.proposal.applicant, referral.referral, sender=sender)

def send_referral_recall_email_notification(referral,request):
    email = ReferralRecallNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-referral-detail',kwargs={'proposal_pk':referral.proposal.id,'referral_pk':referral.id}))

    context = {
        'proposal': referral.proposal,
        'url': url,
    }

    msg = email.send(referral.referral.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_referral_email(msg, referral, sender=sender)
    _log_org_email(msg, referral.proposal.applicant, referral.referral, sender=sender)


def send_referral_complete_email_notification(referral,request):
    email = ReferralCompleteNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': referral.proposal.id}))

    context = {
        'proposal': referral.proposal,
        'url': url,
        'referral_comments': referral.referral_text
    }

    msg = email.send(referral.sent_by.email, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_referral_email(msg, referral, sender=sender)
    _log_org_email(msg, referral.proposal.applicant, referral.referral, sender=sender)


def send_amendment_email_notification(amendment_request, request, proposal):
    email = AmendmentRequestSendNotificationEmail()
    #reason = amendment_request.get_reason_display()
    reason = amendment_request.reason.reason
    url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    if "-internal" in url:
        # remove '-internal'. This email is for external submitters 
        url = ''.join(url.split('-internal'))

    attachments = []
    if amendment_request.amendment_request_documents:
        for doc in amendment_request.amendment_request_documents.all():
            #file_name = doc._file.name
            file_name = doc.name
            attachment = (file_name, doc._file.file.read())
            attachments.append(attachment)


    context = {
        'proposal': proposal,
        'reason': reason,
        'amendment_request_text': amendment_request.text,
        'url': url
    }

    all_ccs = []
    if proposal.applicant.email:
        cc_list = proposal.applicant.email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(proposal.submitter.email, cc=all_ccs, context=context,  attachments=attachments)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_submit_email_notification(request, proposal):
    email = SubmitSendNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id}))
    if "-internal" not in url:
        # add it. This email is for internal staff (assessors)
        url = '-internal.{}'.format(settings.SITE_DOMAIN).join(url.split('.' + settings.SITE_DOMAIN))

    context = {
        'proposal': proposal,
        'url': url
    }

    msg = email.send(proposal.assessor_recipients, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)
    return msg

def send_external_submit_email_notification(request, proposal):
    email = ExternalSubmitSendNotificationEmail()
    url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    if "-internal" in url:
        # remove '-internal'. This email is for external submitters 
        url = ''.join(url.split('-internal'))

    context = {
        'proposal': proposal,
        'submitter': proposal.submitter.get_full_name(),
        'url': url
    }

    all_ccs = []
    if proposal.applicant.email:
        cc_list = proposal.applicant.email
        if cc_list:
            all_ccs = [cc_list]

    msg = email.send(proposal.submitter.email, cc= all_ccs, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)
    return msg

#send email when Proposal is 'proposed to decline' by assessor.
def send_approver_decline_email_notification(reason, request, proposal):
    email = ApproverDeclineSendNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id}))
    context = {
        'proposal': proposal,
        'reason': reason,
        'url': url
    }

    msg = email.send(proposal.approver_recipients, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_approver_approve_email_notification(request, proposal):
    email = ApproverApproveSendNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id}))
    context = {
        'start_date' : proposal.proposed_issuance_approval.get('start_date'),
        'expiry_date' : proposal.proposed_issuance_approval.get('expiry_date'),
        'details': proposal.proposed_issuance_approval.get('details'),
        'proposal': proposal,
        'url': url
    }

    msg = email.send(proposal.approver_recipients, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_proposal_decline_email_notification(proposal,request,proposal_decline):
    email = ProposalDeclineSendNotificationEmail()

    context = {
        'proposal': proposal,

    }
    cc_list = proposal_decline.cc_email
    all_ccs = []
    if cc_list:
        all_ccs = cc_list.split(',')
    if proposal.applicant.email:
        all_ccs.append(proposal.applicant.email)

    msg = email.send(proposal.submitter.email, bcc= all_ccs, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)

def send_proposal_approver_sendback_email_notification(request, proposal):
    email = ApproverSendBackNotificationEmail()
    url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id}))
    context = {
        'proposal': proposal,
        'url': url,
        'approver_comment': proposal.approver_comment
    }

    msg = email.send(proposal.assessor_recipients, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)



def send_proposal_approval_email_notification(proposal,request):
    email = ProposalApprovalSendNotificationEmail()
    if proposal.approval.reissued:
        email.subject= 'Your Approval has been reissued.'

    context = {
        'proposal': proposal,

    }
    cc_list = proposal.proposed_issuance_approval['cc_email']
    all_ccs = []
    if cc_list:
        all_ccs = cc_list.split(',')
    if proposal.applicant.email:
        all_ccs.append(proposal.applicant.email)

    licence_document= proposal.approval.licence_document._file
    if licence_document is not None:
        file_name = proposal.approval.licence_document.name
        attachment = (file_name, licence_document.file.read(), 'application/pdf')
        attachment = [attachment]
    else:
        attachment = []

    msg = email.send(proposal.submitter.email, bcc= all_ccs, attachments=attachment, context=context)
    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)


def send_assessment_reminder_email_notification(proposal):
    email = AssessmentReminderSendNotificationEmail()
    #url = request.build_absolute_uri(reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id}))
    url=settings.SITE_URL if settings.SITE_URL else ''
    url+=reverse('internal-proposal-detail',kwargs={'proposal_pk': proposal.id})
    if "-internal" not in url:
        # add it. This email is for internal staff (assessors)
        url = '-internal.{}'.format(settings.SITE_DOMAIN).join(url.split('.' + settings.SITE_DOMAIN))

    context = {
        'proposal': proposal,
        'url': url
    }

    msg = email.send(proposal.assessor_recipients, context=context)
    #sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    sender = settings.DEFAULT_FROM_EMAIL
    try:
        sender_user = EmailUser.objects.get(email__icontains=sender)
    except:
        EmailUser.objects.create(email=sender, password='')
        sender_user = EmailUser.objects.get(email__icontains=sender)
    _log_proposal_email(msg, proposal, sender=sender_user)
    _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender_user)
    return msg



def _log_proposal_referral_email(email_message, referral, sender=None):
    from disturbance.components.proposals.models import ProposalLogEntry
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
        to = proposal.applicant.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = referral.referral

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'proposal': referral.proposal,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = ProposalLogEntry.objects.create(**kwargs)

    return email_entry





def _log_proposal_email(email_message, proposal, sender=None):
    from disturbance.components.proposals.models import ProposalLogEntry
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
        to = proposal.submitter.email
        fromm = smart_text(sender) if sender else SYSTEM_NAME
        all_ccs = ''

    customer = proposal.submitter

    staff = sender

    kwargs = {
        'subject': subject,
        'text': text,
        'proposal': proposal,
        'customer': customer,
        'staff': staff,
        'to': to,
        'fromm': fromm,
        'cc': all_ccs
    }

    email_entry = ProposalLogEntry.objects.create(**kwargs)

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
