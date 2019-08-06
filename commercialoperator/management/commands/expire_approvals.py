from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from commercialoperator.components.approvals.models import Approval
from ledger.accounts.models import EmailUser
import datetime

import itertools

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Change the status of Approvals to Expired when past expiry date'

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email='cron@dbca.wa.gov.au')
        except:
            user = EmailUser.objects.create(email='cron@dbca.wa.gov.au', password = '')

        today = timezone.localtime(timezone.now()).date()
        logger.info('Running command {}'.format(__name__))
        for a in Approval.objects.filter(status = 'current'):
            if a.expiry_date < today:
                try:
                    a.expire_approval(user)
                    a.save()
                    logger.info('Updated Approval {} status to {}'.format(a.id,a.status))
                except:
                    logger.info('Error updating Approval {} status'.format(a.id))

        logger.info('Command {} completed'.format(__name__))
