from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from disturbance.components.compliances.models import Compliance
import datetime
import itertools

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Change the status of Compliances from future to due when they are close to due date'

    def handle(self, *args, **options):
        today = timezone.now().date()
        timedelta = datetime.timedelta
        compare_date = timedelta(days=14) + today

        logger.info('Running command {}'.format(__name__))
        for c in Compliance.objects.filter(processing_status = 'future'):
            #if(c.due_date<= compare_date<= c.approval.expiry_date) and c.approval.status=='current':
            if(c.due_date<= compare_date) and (c.due_date<= c.approval.expiry_date) and c.approval.status=='current':
                try:
                    c.processing_status='due'
                    c.customer_status='due'
                    c.save()
                    logger.info('updated Compliance {} status to {}'.format(c.id,c.processing_status))
                except:
                    logger.info('Error updating Compliance {} status'.format(c.id))
        logger.info('Command {} completed'.format(__name__))
