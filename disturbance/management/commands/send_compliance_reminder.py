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
    help = 'Send reminder notification for compliances which has past due dates'

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email='cron@dbca.wa.gov.au')
        except:
            user = EmailUser.objects.create(email='cron@dbca.wa.gov.au', password = '')

        today = timezone.now().date()
        logger.info('Running command {}'.format(__name__))
        for c in Compliance.objects.filter(processing_status = 'due'):
            if c.due_date < today:
                if c.lodgement_date==None and c.reminder_sent==False:
                    try:
                        c.send_reminder(user)
                        c.save()
                        logger.info('Reminder sent for Compliance {} '.format(c.id))
                    except Exception as e:
                        logger.info('Error sending Reminder Compliance {} '.format(c.id))

        logger.info('Command {} completed'.format(__name__))
