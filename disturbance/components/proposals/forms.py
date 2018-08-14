from django import forms
from django.core.exceptions import ValidationError
from ledger.accounts.models import EmailUser
from disturbance.components.proposals.models import ProposalAssessorGroup,ProposalApproverGroup, HelpPage
from disturbance.components.main.models import SystemMaintenance
from ckeditor.widgets import CKEditorWidget
from django.conf import settings
import pytz
from datetime import datetime, timedelta


class ProposalAssessorGroupAdminForm(forms.ModelForm):
    class Meta:
        model = ProposalAssessorGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProposalAssessorGroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            #self.fields['members'].queryset = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
            self.fields['members'].queryset = EmailUser.objects.filter(is_staff=True)

    def clean(self):
        super(ProposalAssessorGroupAdminForm, self).clean()
        if self.instance and ProposalAssessorGroup.objects.all().exists():
            try:
                original_members = ProposalAssessorGroup.objects.get(id=self.instance.id).members.all()
                current_members = self.cleaned_data.get('members')
                for o in original_members:
                    if o not in current_members:
                        if self.instance.member_is_assigned(o):
                            raise ValidationError('{} is currently assigned to a proposal(s)'.format(o.email))
            except:
                pass


class ProposalApproverGroupAdminForm(forms.ModelForm):
    class Meta:
        model = ProposalApproverGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProposalApproverGroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            #self.fields['members'].queryset = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
            self.fields['members'].queryset = EmailUser.objects.filter(is_staff=True)

    def clean(self):
        super(ProposalApproverGroupAdminForm, self).clean()
        if self.instance:
            try:
                original_members = ProposalApproverGroup.objects.get(id=self.instance.id).members.all()
                current_members = self.cleaned_data.get('members')
                for o in original_members:
                    if o not in current_members:
                        if self.instance.member_is_assigned(o):
                            raise ValidationError('{} is currently assigned to a proposal(s)'.format(o.email))
            except:
                pass


class DisturbanceHelpPageAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = HelpPage
        fields = '__all__'


class SystemMaintenanceAdminForm(forms.ModelForm):
    class Meta:
        model = SystemMaintenance
        fields = '__all__'

    def clean(self):
        cleaned_data = self.cleaned_data
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        try:
            latest_obj = SystemMaintenance.objects.exclude(id=self.instance.id).latest('start_date')
        except: 
            latest_obj = SystemMaintenance.objects.none()
        tz_local = pytz.timezone(settings.TIME_ZONE) #start_date.tzinfo
        tz_utc = pytz.timezone('utc') #latest_obj.start_date.tzinfo

        if latest_obj:
            latest_end_date = latest_obj.end_date.astimezone(tz=tz_local)
            if self.instance.id:
                if start_date < latest_end_date and start_date < self.instance.start_date.astimezone(tz_local):
                    raise forms.ValidationError('Start date cannot be before an existing records latest end_date. Start Date must be after {}'.format(latest_end_date.ctime()))
            else:
                if start_date < latest_end_date:
                    raise forms.ValidationError('Start date cannot be before an existing records latest end_date. Start Date must be after {}'.format(latest_end_date.ctime()))

        if self.instance.id:
            if start_date < datetime.now(tz=tz_local) - timedelta(minutes=5) and start_date < self.instance.start_date.astimezone(tz_local):
                raise forms.ValidationError('Start date cannot be edited to be further in the past')
        else:
            if start_date < datetime.now(tz=tz_local) - timedelta(minutes=5):
                raise forms.ValidationError('Start date cannot be in the past')

        if end_date < start_date:
            raise forms.ValidationError('End date cannot be before start date')

        super(SystemMaintenanceAdminForm, self).clean()
        return cleaned_data


