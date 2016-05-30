import os
from datetime import datetime

from django import forms

from wildlifelicensing.apps.main.models import WildlifeLicence

DATE_FORMAT = '%d/%m/%Y'


class IdentificationForm(forms.Form):
    VALID_FILE_TYPES = ['png', 'jpg', 'jpeg', 'gif', 'pdf']

    identification_file = forms.FileField(label='Image containing Identification', help_text='E.g. drivers licence, passport, proof-of-age')

    def clean_identification_file(self):
        id_file = self.cleaned_data.get('identification_file')

        ext = os.path.splitext(str(id_file))[1][1:]

        if ext not in self.VALID_FILE_TYPES:
            raise forms.ValidationError('Uploaded image must be of file type: %s' % ', '.join(self.VALID_FILE_TYPES))

        return id_file


class IssueLicenceForm(forms.ModelForm):
    class Meta:
        model = WildlifeLicence
        fields = ['issue_date', 'start_date', 'end_date', 'is_renewable', 'purpose', 'cover_letter_message']

    def __init__(self, *args, **kwargs):
        purpose = kwargs.pop('purpose', None)

        is_renewable = kwargs.pop('is_renewable', False)

        super(IssueLicenceForm, self).__init__(*args, **kwargs)

        if purpose is not None:
            self.fields['purpose'].initial = purpose

        if 'instance' not in kwargs:
            today_date = datetime.now()
            self.fields['issue_date'].initial = today_date.strftime(DATE_FORMAT)
            self.fields['start_date'].initial = today_date.strftime(DATE_FORMAT)
    
            self.fields['issue_date'].localize = False
    
            try:
                one_year_today = today_date.replace(year=today_date.year + 1)
            except ValueError:
                one_year_today = today_date + (datetime.date(today_date.year + 1, 1, 1) - datetime.date(today_date.year, 1, 1))
    
            self.fields['end_date'].initial = one_year_today.strftime(DATE_FORMAT)
    
            self.fields['is_renewable'].initial = is_renewable
            self.fields['is_renewable'].widget = forms.CheckboxInput()
