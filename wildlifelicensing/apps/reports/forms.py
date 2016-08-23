from django import forms
from datetime import datetime, date

from django.forms.widgets import SelectMultiple
from wildlifelicensing.apps.main.models import Region


class ReportForm(forms.Form):
    from_date = forms.DateField(required=True)
    to_date = forms.DateField(required=True)
    regions = forms.ModelMultipleChoiceField(queryset=Region.objects.all(),
                                             required=False,
                                             widget=SelectMultiple(
                                                 attrs={"class": "hidden"}
                                             ))

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)

        today = datetime.today()

        if today.month < 7:
            self.fields['from_date'].initial = date(today.year - 1, 7, 1)
            self.fields['to_date'].initial = date(today.year, 6, 30)
        else:
            self.fields['from_date'].initial = date(today.year, 7, 1)
            self.fields['to_date'].initial = date(today.year + 1, 6, 30)