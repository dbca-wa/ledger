from datetime import date, timedelta

from django_cron import CronJobBase, Schedule

from wildlifecompliance.components.returns.models import Return


class CheckDueReturnsCronJob(CronJobBase):
    """
    Set Due status for return seven days before it is due.
    """
    RUN_AT_TIMES = ['00:00']
    DUE_DAYS = 7

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'returns.check_due_status'

    def do(self):
        due_date = date.today() + timedelta(days=self.DUE_DAYS)
        for ret in Return.objects.filter(
            due_date=due_date,
            processing_status__in=[
                'draft',
                'future']):
            ret.customer_status = 'due'
            ret.save
