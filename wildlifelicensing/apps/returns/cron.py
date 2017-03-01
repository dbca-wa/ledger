from datetime import date, timedelta

from django_cron import CronJobBase, Schedule

from wildlifelicensing.apps.returns.models import Return
from wildlifelicensing.apps.returns.emails import send_return_overdue_email_notification, \
    send_return_overdue_staff_email_notification


class CheckOverdueReturnsCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']
    OVERDUE_DAYS_FIRST_REMINDER = 1
    OVERDUE_DAYS_SECOND_REMINDER = 7

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'returns.check_overdue_returns'

    def do(self):
        # first reminder that is sent to licence holder
        due_date = date.today() - timedelta(days=self.OVERDUE_DAYS_FIRST_REMINDER)

        for ret in Return.objects.filter(due_date=due_date).exclude(status__in=['submitted', 'accepted']):
            send_return_overdue_email_notification(ret)

        # second notice that is sent to staff
        due_date = date.today() - timedelta(days=self.OVERDUE_DAYS_SECOND_REMINDER)

        for ret in Return.objects.filter(due_date=due_date).exclude(status__in=['submitted', 'accepted']):
            send_return_overdue_staff_email_notification(ret)
