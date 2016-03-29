from django import forms

from ledger.accounts.models import Persona


class PersonaSelectionForm(forms.Form):
    persona = forms.ModelChoiceField(queryset=Persona.objects.none(), empty_label=None)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')

        selected_persona = None
        if 'selected_persona' in kwargs:
            selected_persona = kwargs.pop('selected_persona')

        super(PersonaSelectionForm, self).__init__(*args, **kwargs)

        self.fields['persona'].queryset = user.persona_set.all()

        if selected_persona is not None:
            self.fields['persona'].initial = selected_persona
        else:
            self.fields['persona'].initial = user.persona_set.first()
