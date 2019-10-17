from datetime import date, timedelta

from django.db.models import Q

from django_cron import CronJobBase, Schedule

from wildlifelicensing.apps.applications.models import Assessment
from wildlifelicensing.apps.applications.emails import send_assessment_reminder_email


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
