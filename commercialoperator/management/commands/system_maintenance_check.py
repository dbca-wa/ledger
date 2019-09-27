from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import os
from commercialoperator.components.main.models import SystemMaintenance
from commercialoperator.templatetags.users import system_maintenance_can_start

import itertools

import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Excecuted from cron, eg:
        SHELL=/bin/bash
        # Execute every minute. Polls the commercialoperator Admin table SystemMaintenance, and checks if the application can be taken down at the time indicated in the Admin table
        * * * * * root cd /var/www/ubuntu-1604/app-grp1/commercialoperator_prod.8094  && source venv/bin/activate && python manage_ds.py system_maintenance_check >/dev/null 2>&1

    CMD's eg:
        mv /var/www/ubuntu-1604/cfg-grp1/commercialoperator_prod.8094.ini /var/www/ubuntu-1604/cfg-grp1/commercialoperator_prod.8094.ini.bak
    """

    help = 'Check if System Maintenance is due, and terminate uwsgi/supervisor process'
    log_file = os.getcwd() + '/logs/sys_maintenance.log'

    def handle(self, *args, **options):
        cmd = 'mv /var/www/ubuntu-1604/cfg-grp1/commercialoperator_prod.8094.ini /var/www/ubuntu-1604/cfg-grp1/commercialoperator_prod.8094.ini.bak 2>&1 | tee -a {}'.format(self.log_file)
        if system_maintenance_can_start():
            logger.info('Running command {}'.format(__name__))
            subprocess.Popen('date 2>&1 | tee -a {}'.format(self.log_file), shell=True)
            #subprocess.Popen(settings.SUPERVISOR_STOP_CMD + ' 2>&1 | tee -a {}'.format(self.log_file), shell=True)
            subprocess.Popen(cmd, shell=True)

