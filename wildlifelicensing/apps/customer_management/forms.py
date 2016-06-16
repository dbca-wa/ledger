from django import forms

from ledger.accounts.models import EmailUser


class CustomerSearchForm(forms.Form):
    search = forms.CharField()


class CustomerDetailsForm(forms.ModelForm):
    identification = forms.FileField(label='Photo Identification', required=False)

    class Meta:
        model = EmailUser
        fields = ['first_name', 'last_name', 'title', 'dob', 'email', 'phone_number', 'mobile_number', 'fax_number',
                  'character_flagged', 'character_comments']
