from datetime import date, timedelta

from django_cron import CronJobBase, Schedule

from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.main.emails import send_licence_renewal_email_notification


class CheckLicenceRenewalsCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']
    LICENCE_RENEWAL_NOTIFICATION_DAYS = 30

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'main.check_licence_renewals'

    def do(self):
        expiry_notification_date = date.today() + timedelta(days=self.LICENCE_RENEWAL_NOTIFICATION_DAYS)

        renewal_conditions = {
            'end_date__lte': expiry_notification_date,
            'is_renewable': True,
            'renewal_sent': False,
            'replaced_by__isnull': True
        }

        for licence in WildlifeLicence.objects.filter(**renewal_conditions):
            if send_licence_renewal_email_notification(licence):
                licence.renewal_sent = True
                licence.save()
