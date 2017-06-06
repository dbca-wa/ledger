from django import forms

from wildlifelicensing.apps.main.forms import CommunicationsLogEntryForm
from wildlifelicensing.apps.returns.models import ReturnLogEntry, ReturnAmendmentRequest


class NilReturnForm(forms.Form):
    comments = forms.CharField(label='Nil Return Comments',
                               help_text="Please provide the reasons why you're not providing return data. ",
                               widget=forms.Textarea(attrs={'cols': 40, 'rows': 2})
                               )


class UploadSpreadsheetForm(forms.Form):
    spreadsheet_file = forms.FileField(label='Upload Excel Spreadsheet',
                                       help_text='Upload Excel spreadsheet of returns in xlsx format')


class ReturnsLogEntryForm(CommunicationsLogEntryForm):
    class Meta:
        model = ReturnLogEntry
        fields = ['to', 'fromm', 'type', 'subject', 'text', 'attachment']


class ReturnAmendmentRequestForm(forms.ModelForm):
    class Meta:
        model = ReturnAmendmentRequest
        fields = ['ret', 'officer', 'reason']
        widgets = {'ret': forms.HiddenInput(), 'officer': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        ret = kwargs.pop('ret', None)
        officer = kwargs.pop('officer', None)

        super(ReturnAmendmentRequestForm, self).__init__(*args, **kwargs)

        if ret is not None:
            self.fields['ret'].initial = ret

        if officer is not None:
            self.fields['officer'].initial = officer
