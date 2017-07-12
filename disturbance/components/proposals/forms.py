from django import forms
from ledger.accounts.models import EmailUser
from disturbance.components.proposals.models import ProposalAssessorGroup

class ProposalAssessorGroupAdminForm(forms.ModelForm):
    class Meta:
        model = ProposalAssessorGroup
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProposalAssessorGroupAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['members'].queryset = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
