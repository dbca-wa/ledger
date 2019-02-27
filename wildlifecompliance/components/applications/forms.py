from django import forms
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.applications.models import ApplicationGroupType


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
