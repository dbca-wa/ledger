from datetime import date, timedelta

from django_cron import CronJobBase, Schedule

from wildlifelicensing.apps.returns.models import Return
from wildlifelicensing.apps.returns.emails import send_return_overdue_email_notification


class CheckOverdueReturnsCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'returns.check_overdue_returns'

    def do(self):
        yesterday = date.today() - timedelta(days=1)

        for ret in Return.objects.filter(due_date=yesterday).exclude(status='submitted').exclude(status='accepted'):
            send_return_overdue_email_notification(ret)
