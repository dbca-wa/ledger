from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from ledger.accounts.models import EmailUser
from disturbance.components.compliances.models import Compliance, ComplianceUserAction
from disturbance.components.compliances.email import send_due_email_notification, send_internal_due_email_notification
import datetime
import itertools

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Change the status of Compliances from future to due when they are close to due date'

    def handle(self, *args, **options):
        today = timezone.localtime(timezone.now()).date()
        compare_date = today + datetime.timedelta(days=14)

        try:
            user = EmailUser.objects.get(email='cron@dbca.wa.gov.au')
        except:
            user = EmailUser.objects.create(email='cron@dbca.wa.gov.au', password = '')

        logger.info('Running command {}'.format(__name__))
        for c in Compliance.objects.filter(processing_status = 'future'):
            #if(c.due_date<= compare_date<= c.approval.expiry_date) and c.approval.status=='current':
            if(c.due_date<= compare_date) and (c.due_date<= c.approval.expiry_date) and c.approval.status=='current':
                try:
                    c.processing_status='due'
                    c.customer_status='due'
                    c.save()
                    ComplianceUserAction.log_action(c,ComplianceUserAction.ACTION_STATUS_CHANGE.format(c.id),user)
                    logger.info('updated Compliance {} status to {}'.format(c.id,c.processing_status))
                except:
                    logger.info('Error updating Compliance {} status'.format(c.id))
        logger.info('Command {} completed'.format(__name__))
