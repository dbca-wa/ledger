from datetime import date, timedelta

from django.db.models import Q
from django.core import management
from django_cron import CronJobBase, Schedule

from commercialoperator.components.bookings.utils import oracle_integration


class OracleIntegrationCronJob(CronJobBase):
    """
    To Test (shortly after RUN_AT_TIMES):
        ./manage_co.py runcrons
    """
    RUN_AT_TIMES = ['01:05']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'cols.oracle_integration'

    def do(self):
        oracle_integration(str(date.today()-timedelta(days=1)),False)

