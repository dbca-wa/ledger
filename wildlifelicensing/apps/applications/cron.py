from datetime import date, timedelta

from django.db.models import Q

from django_cron import CronJobBase, Schedule

from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.applications.models import Assessment
from wildlifelicensing.apps.applications.emails import send_licence_renewal_email_notification, \
    send_assessment_reminder_email


class CheckLicenceRenewalsCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']
    LICENCE_RENEWAL_NOTIFICATION_DAYS = 30

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'applications.check_licence_renewals'

    def do(self):
        expiry_notification_date = date.today() + timedelta(days=self.LICENCE_RENEWAL_NOTIFICATION_DAYS)

        for licence in WildlifeLicence.objects.filter(end_date=expiry_notification_date, is_renewable=True):
            send_licence_renewal_email_notification(licence)


class AssessmentRemindersCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']
    ASSESSMENT_REMINDER_NOTIFICATION_DAYS = 7

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'applications.assessment_reminders'

    def do(self):
        expiry_notification_date = date.today() - timedelta(days=self.ASSESSMENT_REMINDER_NOTIFICATION_DAYS)

        q = Q(date_last_reminded__lte=expiry_notification_date) | Q(date_last_reminded__isnull=True)
        q &= Q(status='awaiting_assessment')

        for assessment in Assessment.objects.filter(q):
            send_assessment_reminder_email(assessment)
            assessment.date_last_reminded = date.today()
            assessment.save()
