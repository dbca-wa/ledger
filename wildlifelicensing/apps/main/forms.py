import os
from datetime import datetime

from django import forms
from django.conf import settings

from wildlifelicensing.apps.main.models import WildlifeLicence


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
        fields = ['issue_date', 'start_date', 'end_date', 'purpose']    

    def __init__(self, *args, **kwargs):
        purpose = kwargs.pop('purpose', None)

        super(IssueLicenceForm, self).__init__(*args, **kwargs)

        if purpose is not None:
            self.fields['purpose'].initial = purpose

        self.fields['issue_date'].initial = datetime.now()
        self.fields['issue_date'].input_formats =  ('%d/%m/%Y',)

