from datetime import date, timedelta

from django.db.models import Q
from django.core import management
from django_cron import CronJobBase, Schedule

from mooring.models import Booking, MooringsiteRate, MooringAreaGroup, GlobalSettings, MooringArea
from mooring.reports import outstanding_bookings
from mooring.emails import send_booking_confirmation, send_booking_period_email
from mooring.utils import oracle_integration

class UnpaidBookingsReportCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:30']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'mooring.unpaid_bookings_report'

    def do(self):
        outstanding_bookings() 

class OracleIntegrationCronJob(CronJobBase):
    RUN_AT_TIMES = ['00:30']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'mooring.oracle_integration'

    def do(self):
        oracle_integration(str(date.today()-timedelta(days=1)),False)

class SendBookingsConfirmationCronJob(CronJobBase):
    RUN_EVERY_MINS = 5

    schedule = Schedule(run_at_times=RUN_EVERY_MINS)
    code = 'mooring.send_booking_confirmations'

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

class CheckMooringsNoBookingPeriod(CronJobBase):
    RUN_AT_TIMES = ['00:30']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code= 'mooring.booking_period_check'

    def do(self):
        for group in MooringAreaGroup.objects.all():
            moorings_no_booking = []
            moorings_with_bookings = []
            moorings = group.moorings.all()
            days = int(GlobalSettings.objects.get(mooring_group=group, key=2).value) + 11
            date_to = date.today() + timedelta(days=days)
            for mooring in moorings:
                rates = MooringsiteRate.objects.filter(campsite__mooringarea=mooring)
                future_rates = rates.filter(date_start__gte=date.today(), date_end__lte=date_to).order_by('date_start')
                last_rate = rates.filter(Q(date_end__gte=date_to) | Q(date_end=None)).order_by('date_end').first()
                current_rate = rates.filter(Q(date_start__lte=date.today()), Q(date_end__gte=date.today()) | Q(date_end=None)).order_by('date_start')
                failed = False
                if current_rate.count() == 1:
                    end = current_rate[0].date_end
                    start = None
                    for rate in future_rates:
                        start = rate.date_start
                        if start == end + timedelta(days=1):
                            end = rate.date_end
                        else:
                            moorings_no_booking.append(mooring)
                            failed = True
                    if last_rate and not failed:
                        if last_rate.date_end:
                            if last_rate.date_start == end + timedelta(days=1):
                                moorings_with_bookings.append(mooring)
                            else:
                                moorings_no_booking.append(mooring)
                        else:
                            moorings_with_bookings.append(mooring)
                    elif not failed:
                        moorings_no_booking.append(mooring)
                else:
                    moorings_no_booking.append(mooring)
            if len(moorings_no_booking) > 0:
                send_booking_period_email(moorings_no_booking, group, days-1)

class RegisteredVesselsImport(CronJobBase):
    RUN_AT_TIMES = ['00:30']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code='mooring.registered_vessels'

    def do(self):
        path = '/mnt/lotusnotes_dump/'
        management.call_command('lotus_notes_vessels', path)
