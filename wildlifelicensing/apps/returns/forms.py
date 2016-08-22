from django import forms


class NilReturnForm(forms.Form):
    comments = forms.CharField(label='Comments',
                               help_text="Please provide the reasons why you're not providing any return. ",
                               widget=forms.Textarea(attrs={'cols': 40, 'rows': 4})
                               )


class UploadSpreadsheetForm(forms.Form):
    spreadsheet_file = forms.FileField(label='Upload Excel Spreadsheet',
                                       help_text='Upload Excel spreadsheet of returns in xlsx format')
