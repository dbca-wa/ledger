from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from ledger.accounts.models import EmailUser
from commercialoperator.components.bookings.utils import create_monthly_invoice
from commercialoperator.components.bookings.email import send_monthly_invoices_failed_tclass
import datetime

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run the Invoice Payment Due Notification Script - generates emails to licence holder and assessor for all invoices that are due today, and not yet paid'

    def handle(self, *args, **options):
        bookings = Booking.objects.filter(
            invoices__isnull=False,
            invoices__payment_due_notification_sent=False,
            booking_type__in=[Booking.BOOKING_TYPE_BPAY, Booking.BOOKING_TYPE_MONTHLY_INVOICING]
        )

        overdue_bookings = []
        for booking in bookings:
            try:
                bi = booking.invoices.last()
                if bi.overdue:
                    logger.info('Command {}. Sending payment due notification for BookingInvoice {}'.format(__name__, bi))
                    send_invoice_payment_due_tclass_external_email_notification(user, booking, recipients=[booking.proposal.applicant_email])
                    ProposalUserAction.log_action(booking.proposal,ProposalUserAction.ACTION_SEND_PAYMENT_DUE_NOTIFICATION.format(booking.proposal.id),booking.proposal.applicant_email)
                    bi.payment_due_notification_sent = True
                    bi.save()
                    overdue_bookings.append(booking)
            except Exception, e:
                logger.info('Command {}. Sending payment due notification failed for BookingInvoice {}. {}'.format(__name__, bi, e))

        if overdue_bookings:
            logger.info('Command {}. Send overdue invoices list to assessors {}'.format(__name__, overdue_bookings))
            send_invoice_payment_due_tclass_email_notification(user, bookings, recipients=booking.proposal.assessor_recipients)

        logger.info('Command {} completed'.format(__name__))

