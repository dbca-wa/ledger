from datetime import date, timedelta
from django_cron import CronJobBase, Schedule
from parkstay.models import Booking
from parkstay.reports import outstanding_bookings
from parkstay.emails import send_booking_confirmation
from parkstay.utils import oracle_integration


class UnpaidBookingsReportCronJob(CronJobBase):
    RUN_AT_TIMES = ['01:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'parkstay.unpaid_bookings_report'

    def do(self):
        outstanding_bookings()


class OracleIntegrationCronJob(CronJobBase):
    RUN_AT_TIMES = ['01:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'parkstay.oracle_integration'

    def do(self):
        oracle_integration(str(date.today() - timedelta(days=1)), False)


class SendBookingsConfirmationCronJob(CronJobBase):
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_at_times=RUN_EVERY_MINS)
    code = 'parkstay.send_booking_confirmations'

    def do(self):
        try:
            # Update confirmation_status
            for b in Booking.objects.all():
                if not b.paid and b.confirmation_sent:
                    b.confirmation_sent = False
                    b.save()

            unconfirmed = Booking.objects.filter(confirmation_sent=False)
            if unconfirmed:
                for b in unconfirmed:
                    if b.paid:
                        send_booking_confirmation(b)
        except:
            raise
