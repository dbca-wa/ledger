from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from commercialoperator.components.approvals.models import Approval
from ledger.accounts.models import EmailUser
import datetime

import itertools
import subprocess

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run the Commercial Operator Cron tasks'

    def handle(self, *args, **options):
        logger.info('Running command {}'.format(__name__))
        subprocess.call('python manage_co.py update_compliance_status', shell=True) 
        subprocess.call('python manage_co.py send_compliance_reminder', shell=True) 
        subprocess.call('python manage_co.py update_approval_status', shell=True) 
        subprocess.call('python manage_co.py expire_approvals', shell=True) 
        subprocess.call('python manage_co.py approval_renewal_notices', shell=True) 
        logger.info('Command {} completed'.format(__name__))
