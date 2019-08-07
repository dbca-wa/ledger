import datetime
import pytz
from dateutil.relativedelta import relativedelta, FR


from django import forms
from django.utils import timezone


class PaymentsReportForm(forms.Form):
    date_format = '%d/%m/%Y %H:%M:%S'
    start = forms.DateTimeField(required=True, widget=forms.DateTimeInput(
        format=date_format
    ))
    end = forms.DateTimeField(required=True, widget=forms.DateTimeInput(
        format=date_format
    ))
    banked_start = forms.DateTimeField(required=True, widget=forms.DateTimeInput(
        format=date_format
    ))
    banked_end = forms.DateTimeField(required=True, widget=forms.DateTimeInput(
        format=date_format
    ))

    def __init__(self, *args, **kwargs):
        super(PaymentsReportForm, self).__init__(*args, **kwargs)
        # initial datetime spec:
        # end set to be the last Friday at 10:00 pm AEST even if it is a Friday
        # start exactly one week before end

        now = timezone.localtime(timezone.now())
        # create a timezone aware datetime at 10:00 pm AEST
        today_ten_pm_aest = timezone.make_aware(
            datetime.datetime(now.year, now.month, now.day, 22, 0),
            timezone=pytz.timezone('Australia/Sydney'))
        # convert to local
        today_ten_pm_aest_local = timezone.localtime(today_ten_pm_aest)
        # back to previous friday (even if we are friday)
        delta = relativedelta(weekday=FR(-1)) \
            if today_ten_pm_aest_local.weekday() != FR.weekday else relativedelta(weekday=FR(-2))
        end = today_ten_pm_aest_local + delta
        start = end + relativedelta(weeks=-1)

        banked_start =  (start - datetime.timedelta(days=start.weekday())).replace(hour=0, minute=0)
        banked_end = (banked_start + datetime.timedelta(days=6)).replace(hour=23, minute=59, second=59)

        self.fields['start'].initial = start
        self.fields['end'].initial = end
        self.fields['banked_start'].initial = banked_start
        self.fields['banked_end'].initial = banked_end
