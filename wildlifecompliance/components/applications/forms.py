from django import forms
from django.core.exceptions import ValidationError
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.applications.models import ApplicationAssessorGroup,ApplicationApproverGroup,ApplicationGroupType, ApplicationActivityType

class ApplicationAssessorGroupAdminForm(forms.ModelForm):
    class Meta:
        model = ApplicationAssessorGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ApplicationAssessorGroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['members'].queryset = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')

    def clean(self):
        super(ApplicationAssessorGroupAdminForm, self).clean()
        if self.instance:
            original_members = ApplicationAssessorGroup.objects.get(id=self.instance.id).members.all()
            current_members = self.cleaned_data.get('members')
            for o in original_members:
                if o not in current_members:
                    if self.instance.member_is_assigned(o):
                        raise ValidationError('{} is currently assigned to a application(s)'.format(o.email))

class ApplicationApproverGroupAdminForm(forms.ModelForm):
    class Meta:
        model = ApplicationApproverGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ApplicationApproverGroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['members'].queryset = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')

    def clean(self):
        super(ApplicationApproverGroupAdminForm, self).clean()
        if self.instance:
            original_members = ApplicationApproverGroup.objects.get(id=self.instance.id).members.all()
            current_members = self.cleaned_data.get('members')
            for o in original_members:
                if o not in current_members:
                    if self.instance.member_is_assigned(o):
                        raise ValidationError('{} is currently assigned to a application(s)'.format(o.email))

class ApplicationGroupTypeAdminForm(forms.ModelForm):
    class Meta:
        model = ApplicationGroupType
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ApplicationGroupTypeAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['members'].queryset = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')

    def clean(self):
        super(ApplicationGroupTypeAdminForm, self).clean()
        # if self.instance:
        #     # original_members = ApplicationGroupType.objects.get(id=self.instance.id).members.all()
        #     current_members = self.cleaned_data.get('members')
        #     for o in original_members:
        #         if o not in current_members:
        #             if self.instance.member_is_assigned(o):
        #                 raise ValidationError('{} is currently assigned to a application(s)'.format(o.email))


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
