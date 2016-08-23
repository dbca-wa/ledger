from django import forms


class NilReturnForm(forms.Form):
    comments = forms.CharField(label='Nil Return Comments',
                               help_text="Please provide the reasons why you're not providing return data. ",
                               widget=forms.Textarea(attrs={'cols': 40, 'rows': 2})
                               )


class UploadSpreadsheetForm(forms.Form):
    spreadsheet_file = forms.FileField(label='Upload Excel Spreadsheet',
                                       help_text='Upload Excel spreadsheet of returns in xlsx format')
