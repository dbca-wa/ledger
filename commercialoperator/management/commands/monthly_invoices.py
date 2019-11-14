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
    help = 'Run the Monthly Invoices Script - generates invoices per licence/org_applicant for previous month'

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email='cron@dbca.wa.gov.au')
        except:
            user = EmailUser.objects.create(email='cron@dbca.wa.gov.au', password = '')

        logger.info('Running command {}'.format(__name__))
        failed_bookings = create_monthly_invoice(user, offset_months=-1)

        if failed_bookings:
            # some invoices failed
            logger.info('Command {} failed. Invoice failed to generate for booking IDs {}'.format(__name__, ret))
            send_monthly_invoices_failed_tclass(failed_bookings)
        logger.info('Command {} completed'.format(__name__))
