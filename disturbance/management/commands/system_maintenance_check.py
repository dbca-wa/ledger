from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import os
from disturbance.components.main.models import SystemMaintenance
from disturbance.templatetags.users import system_maintenance_can_start

import itertools

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Excecuted from cron, eg:
        SHELL=/bin/bash
        # Execute every minute. Polls the Disturbance Admin table SystemMaintenance, and checks if the application can be taken down at the time indicated in the Admin table
        * * * * * root cd /var/www/disturbance-dev2 && source venv/bin/activate && python manage_ds.py system_maintenance_check >/dev/null 2>&1

    CMD's eg:
        SUPERVISOR_STOP_CMD="supervisorctl stop disturbance-dev"
        SUPERVISOR_STOP_CMD="pkill -f 8499"
    """

    help = 'Check if System Maintenance is due, and terminate uwsgi/supervisor process'
    log_file = os.getcwd() + '/logs/sys_maintenance.log'

    def handle(self, *args, **options):
        if system_maintenance_can_start():
            logger.info('Running command {}'.format(__name__))
            subprocess.Popen('date 2>&1 | tee -a {}'.format(self.log_file), shell=True)
            subprocess.Popen(settings.SUPERVISOR_STOP_CMD + ' 2>&1 | tee -a {}'.format(self.log_file), shell=True)

