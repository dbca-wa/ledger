from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from disturbance.components.compliances.models import Compliance
from ledger.accounts.models import EmailUser
import datetime

import itertools

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send notification emails for compliances which has past due dates, and also reminder notification emails for those that are within the daterange prior to due_date (eg. within 14 days of due date)'

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email='cron@dbca.wa.gov.au')
        except:
            user = EmailUser.objects.create(email='cron@dbca.wa.gov.au', password = '')

        today = timezone.localtime(timezone.now()).date()
        logger.info('Running command {}'.format(__name__))
        for c in Compliance.objects.filter(processing_status = 'due'):
            try:
                c.send_reminder(user)
                c.save()
            except Exception as e:
                logger.info('Error sending Reminder Compliance {}\n{}'.format(c.lodgement_number, e))

        logger.info('Command {} completed'.format(__name__))
