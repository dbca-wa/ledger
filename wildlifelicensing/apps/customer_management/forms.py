from django import forms

from ledger.accounts.models import EmailUser


class CustomerSearchForm(forms.Form):
    search = forms.CharField()


class CustomerDetailsForm(forms.ModelForm):
    identification = forms.FileField(label='Photo Identification', required=False)
    senior_card = forms.FileField(label='Senior Card', required=False)

    def __init__(self, *args, **kwargs):
        super(CustomerDetailsForm, self).__init__(*args, **kwargs)
        if self.instance:
            customer = self.instance
            if not customer.is_senior:
                del self.fields['senior_card']

    class Meta:
        model = EmailUser
        fields = ['first_name', 'last_name', 'title', 'dob', 'email', 'phone_number', 'mobile_number', 'fax_number',
                  'character_flagged', 'character_comments']
