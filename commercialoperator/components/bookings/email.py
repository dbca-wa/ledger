import logging

from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.utils.encoding import smart_text
from django.core.urlresolvers import reverse
from django.conf import settings

from commercialoperator.components.emails.emails import TemplateEmailBase
from commercialoperator.components.bookings.invoice_pdf import create_invoice_pdf_bytes
from commercialoperator.components.bookings.confirmation_pdf import create_confirmation_pdf_bytes
from commercialoperator.components.bookings.models import Booking

logger = logging.getLogger(__name__)

SYSTEM_NAME = settings.SYSTEM_NAME_SHORT + ' Automated Message'

class ApplicationFeeInvoiceTClassSendNotificationEmail(TemplateEmailBase):
    subject = 'Your application fee invoice.'
    html_template = 'commercialoperator/emails/bookings/tclass/send_application_fee_notification.html'
    txt_template = 'commercialoperator/emails/bookings/tclass/send_application_fee_notification.txt'

class ApplicationFeeConfirmationTClassSendNotificationEmail(TemplateEmailBase):
    subject = 'Your application fee confirmation.'
    html_template = 'commercialoperator/emails/bookings/tclass/send_application_fee_confirmation_notification.html'
    txt_template = 'commercialoperator/emails/bookings/tclass/send_application_fee_confirmation_notification.txt'


class InvoiceTClassSendNotificationEmail(TemplateEmailBase):
    subject = 'Your booking invoice.'
    html_template = 'commercialoperator/emails/bookings/tclass/send_invoice_notification.html'
    txt_template = 'commercialoperator/emails/bookings/tclass/send_invoice_notification.txt'

class ConfirmationTClassSendNotificationEmail(TemplateEmailBase):
    subject = 'Your booking confirmation.'
    html_template = 'commercialoperator/emails/bookings/tclass/send_confirmation_notification.html'
    txt_template = 'commercialoperator/emails/bookings/tclass/send_confirmation_notification.txt'

class MonthlyInvoicesFailedTClassEmail(TemplateEmailBase):
    subject = 'Failed: COLS Monthly Invoices.'
    html_template = 'commercialoperator/emails/bookings/tclass/send_monthly_invoices_failed_notification.html'
    txt_template = 'commercialoperator/emails/bookings/tclass/send_monthly_invoices_failed_notification.txt'

class SendPaymentDueNotificationTClassEmail(TemplateEmailBase):
    subject = 'COLS Monthly/BPAY Bookings Invoices Overdue.'
    html_template = 'commercialoperator/emails/bookings/tclass/send_payment_due_notification.html'
    txt_template = 'commercialoperator/emails/bookings/tclass/send_payment_due_notification.txt'

class SendExternalPaymentDueNotificationTClassEmail(TemplateEmailBase):
    subject = 'Your booking invoice is overdue.'
    html_template = 'commercialoperator/emails/bookings/tclass/send_external_payment_due_notification.html'
    txt_template = 'commercialoperator/emails/bookings/tclass/send_external_payment_due_notification.txt'

class PaymentDueNotificationFailedTClassEmail(TemplateEmailBase):
    subject = 'Failed: COLS Payment Due Notifications'
    html_template = 'commercialoperator/emails/bookings/tclass/send_external_payment_due_notification_failed.html'
    txt_template = 'commercialoperator/emails/bookings/tclass/send_external_payment_due_notification_failed.txt'

def send_application_fee_invoice_tclass_email_notification(request, proposal, invoice, recipients, is_test=False):
    email = ApplicationFeeInvoiceTClassSendNotificationEmail()
    #url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    context = {
        'lodgement_number': proposal.lodgement_number,
        #'url': url,
    }

    filename = 'invoice.pdf'
    doc = create_invoice_pdf_bytes(filename, invoice, proposal)
    attachment = (filename, doc, 'application/pdf')

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
#    try:
#        _log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)
#    except:
#        _log_org_email(msg, proposal.submitter, proposal.submitter, sender=sender)
    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    else:
        _log_user_email(msg, proposal.submitter, proposal.submitter, sender=sender)


def send_application_fee_confirmation_tclass_email_notification(request, application_fee, invoice, recipients, is_test=False):
    email = ApplicationFeeConfirmationTClassSendNotificationEmail()
    #url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    proposal = application_fee.proposal
    context = {
        'lodgement_number': proposal.lodgement_number,
        #'url': url,
    }

    filename = 'confirmation.pdf'
    doc = create_confirmation_pdf_bytes(filename, invoice, application_fee)
    #doc = create_invoice_pdf_bytes(filename, invoice, proposal)
    attachment = (filename, doc, 'application/pdf')

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, proposal, sender=sender)
    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    else:
        _log_user_email(msg, proposal.submitter, proposal.submitter, sender=sender)

def send_invoice_tclass_email_notification(request, booking, invoice, recipients, is_test=False):
    email = InvoiceTClassSendNotificationEmail()
    #url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    context = {
        'booking_number': booking.booking_number,
        #'url': url,
    }

    filename = 'invoice.pdf'
    doc = create_invoice_pdf_bytes(filename, invoice, booking.proposal)
    attachment = (filename, doc, 'application/pdf')

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, booking.proposal, sender=sender)
    #_log_org_email(msg, booking.proposal.applicant, booking.proposal.submitter, sender=sender)
    if booking.proposal.org_applicant:
        _log_org_email(msg, booking.proposal.org_applicant, booking.proposal.submitter, sender=sender)
    else:
        _log_user_email(msg, booking.proposal.submitter, booking.proposal.submitter, sender=sender)

def send_confirmation_tclass_email_notification(request, booking, invoice, recipients, is_test=False):
    email = ConfirmationTClassSendNotificationEmail()
    #url = request.build_absolute_uri(reverse('external-proposal-detail',kwargs={'proposal_pk': proposal.id}))

    context = {
        'booking_number': booking.booking_number,
        #'url': url,
    }

    filename = 'confirmation.pdf'
    doc = create_confirmation_pdf_bytes(filename, invoice, booking)
    attachment = (filename, doc, 'application/pdf')

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    sender = request.user if request else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, booking.proposal, sender=sender)
    #_log_org_email(msg, booking.proposal.applicant, booking.proposal.submitter, sender=sender)
    if booking.proposal.org_applicant:
        _log_org_email(msg, booking.proposal.org_applicant, booking.proposal.submitter, sender=sender)
    else:
        _log_user_email(msg, booking.proposal.submitter, booking.proposal.submitter, sender=sender)

def send_proposal_approval_email_notification(proposal,request):
    email = ProposalApprovalSendNotificationEmail()

    context = {
        'proposal': proposal,

    }
    cc_list = proposal.proposed_issuance_approval['cc_email']
    all_ccs = []
    if cc_list:
        all_ccs = cc_list.split(',')

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
    #_log_org_email(msg, proposal.applicant, proposal.submitter, sender=sender)
    if proposal.org_applicant:
        _log_org_email(msg, proposal.org_applicant, proposal.submitter, sender=sender)
    else:
        _log_user_email(msg, proposal.submitter, proposal.submitter, sender=sender)

def send_monthly_invoice_tclass_email_notification(sender, booking, invoice, recipients, is_test=False):
    email = MonthlyInvoiceTClassSendNotificationEmail()

    context = {
        'booking_number': booking.booking_number,
    }

    filename = 'monthly_invoice.pdf'
    doc = create_invoice_pdf_bytes(filename, invoice, booking.proposal)
    attachment = (filename, doc, 'application/pdf')

    msg = email.send(recipients, attachments=[attachment], context=context)
    if is_test:
        return

    _log_proposal_email(msg, booking.proposal, sender=sender)
    if booking.proposal.org_applicant:
        _log_org_email(msg, booking.proposal.org_applicant, booking.proposal.submitter, sender=sender)
    else:
        _log_user_email(msg, booking.proposal.submitter, booking.proposal.submitter, sender=sender)

def send_monthly_invoices_failed_tclass(booking_ids):
    """ Internal failed notification email for Monthly Invoicing script """
    email = MonthlyInvoicesFailedTClassEmail()

    context = {
        'bookings': Booking.objects.filter(id__in=booking_ids).values_list('id', 'admission_number', 'proposal__lodgement_number', 'proposal__org_applicant__organisation__name'),
    }
    msg = email.send(settings.NOTIFICATION_EMAIL, context=context)

def send_payment_due_notification_failed_tclass(bookings):
    """ Internal failed notification email for Payment Due Notification script """
    email = PaymentDueNotificationFailedTClassEmail()

    context = {
        'bookings': bookings
    }
    msg = email.send(settings.NOTIFICATION_EMAIL, context=context)

def send_invoice_payment_due_tclass_email_notification(sender, bookings, recipients, is_test=False):
    email = SendPaymentDueNotificationTClassEmail()

    context = {
        'bookings': bookings,
    }

    msg = email.send(booking.proposal.submitter.email, context=context)
    #sender = sender if sender else settings.DEFAULT_FROM_EMAIL
    #_log_proposal_email(msg, booking.proposal, sender=sender)
    #if booking.proposal.org_applicant:
    #    _log_org_email(msg, booking.proposal.org_applicant, booking.proposal.submitter, sender=sender)
    #else:
    #    _log_user_email(msg, booking.proposal.submitter, booking.proposal.submitter, sender=sender)

def send_invoice_payment_due_tclass_external_email_notification(sender, booking, recipients, is_test=False):
    email = SendExternalPaymentDueNotificationTClassEmail()

    context = {
        'booking': booking,
    }

    msg = email.send(booking.proposal.submitter.email, context=context)
    sender = sender if sender else settings.DEFAULT_FROM_EMAIL
    _log_proposal_email(msg, booking.proposal, sender=sender)
    if booking.proposal.org_applicant:
        _log_org_email(msg, booking.proposal.org_applicant, booking.proposal.submitter, sender=sender)
    else:
        _log_user_email(msg, booking.proposal.submitter, booking.proposal.submitter, sender=sender)




def _log_proposal_email(email_message, proposal, sender=None):
    from commercialoperator.components.proposals.models import ProposalLogEntry
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
    from commercialoperator.components.organisations.models import OrganisationLogEntry
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
