from django import forms
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.applications.models import (
    ApplicationGroupType,
    ApplicationActivityType
)


class ApplicationGroupTypeAdminForm(forms.ModelForm):
    class Meta:
        model = ApplicationGroupType
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ApplicationGroupTypeAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['members'].queryset = EmailUser.objects.filter(
                email__icontains='@dbca.wa.gov.au')

    def clean(self):
        super(ApplicationGroupTypeAdminForm, self).clean()


class ApplicationActivityTypeForm(forms.ModelForm):
    class Meta:
        model = ApplicationActivityType
        fields = ['activity_name', 'short_name', 'name', 'purpose', 'additional_info','advanced','conditions','issue_date','start_date','expiry_date','to_be_issued','processed']
#    activity_name = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
#    short_name = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
#    name = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
#    purpose = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))

def clean_email(self):
    return self.initial['email']