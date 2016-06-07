from django import forms


class UploadSpreadsheetForm(forms.Form):
    spreadsheet_file = forms.FileField(label='Upload Excel Spreadsheet',
                                       help_text='Upload Excel spreadsheet of returns in xls or xlsx format')
