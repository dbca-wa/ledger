from datetime import datetime, timedelta

from django_cron import CronJobBase, Schedule

from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.applications.emails import send_licence_renewal_email_notification


class CheckLicenceRenewalsCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']
    LICENCE_RENEWAL_NOTIFICATION_DAYS = 30

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'applications.check_licence_renewals'

    def do(self):
        expiry_notification_date = datetime.now() + timedelta(days=self.LICENCE_RENEWAL_NOTIFICATION_DAYS)

        for licence in WildlifeLicence.objects.filter(end_date=expiry_notification_date, licence_type__is_renewable=True):
            send_licence_renewal_email_notification(licence)
