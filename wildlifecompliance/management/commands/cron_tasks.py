from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
import datetime

import subprocess

import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run the Wildlife Compliance Cron tasks'

    def handle(self, *args, **options):
        logger.info('Running command {}'.format(__name__))
        subprocess.call('python manage_wc.py update_workbooks', shell=True)
        logger.info('Command {} completed'.format(__name__))
