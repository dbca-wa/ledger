from django.core.management.base import BaseCommand
from django.conf import settings
from wildlifecompliance.utils.excel_utils import ExcelWriter

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

    help = 'Updates the Excel workbooks for each Licence Category from the Wildlife Compliance system'

    def handle(self, *args, **options):
        logger.info('Running command {}'.format(__name__))
        writer = ExcelWriter()
        writer.update_workbooks()
