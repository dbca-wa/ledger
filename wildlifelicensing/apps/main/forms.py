import os

from django import forms



class IdentificationForm(forms.Form):
    VALID_FILE_TYPES = ['png', 'jpg', 'jpeg', 'gif', 'pdf']

    identification_file = forms.FileField(label='Image containing Identification', help_text='E.g. drivers licence, passport, proof-of-age')

    def clean_identification_file(self):
        id_file = self.cleaned_data.get('identification_file')

        ext = os.path.splitext(str(id_file))[1][1:]

        if not ext in self.VALID_FILE_TYPES:
            raise forms.ValidationError('Uploaded image must be of file type: %s' % ', '.join(self.VALID_FILE_TYPES))

        return id_file
