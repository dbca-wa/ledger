from django import forms
from django.core.exceptions import ValidationError
from ledger.accounts.models import EmailUser
from disturbance.components.proposals.models import ProposalAssessorGroup,ProposalApproverGroup

class ProposalAssessorGroupAdminForm(forms.ModelForm):
    class Meta:
        model = ProposalAssessorGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProposalAssessorGroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['members'].queryset = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')

    def clean(self):
        super(ProposalAssessorGroupAdminForm, self).clean()
        if self.instance:
            original_members = ProposalAssessorGroup.objects.get(id=self.instance.id).members.all()
            current_members = self.cleaned_data.get('members')
            for o in original_members:
                if o not in current_members:
                    if self.instance.member_is_assigned(o):
                        raise ValidationError('{} is currently assigned to a proposal(s)'.format(o.email)) 

class ProposalApproverGroupAdminForm(forms.ModelForm):
    class Meta:
        model = ProposalApproverGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProposalApproverGroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['members'].queryset = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')

    def clean(self):
        super(ProposalApproverGroupAdminForm, self).clean()
        if self.instance:
            original_members = ProposalApproverGroup.objects.get(id=self.instance.id).members.all()
            current_members = self.cleaned_data.get('members')
            for o in original_members:
                if o not in current_members:
                    if self.instance.member_is_assigned(o):
                        raise ValidationError('{} is currently assigned to a proposal(s)'.format(o.email)) 
