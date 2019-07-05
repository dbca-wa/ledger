from django import forms
from django.contrib import admin
from reversion.admin import VersionAdmin

from wildlifecompliance.components.offence import models


@admin.register(models.Offence)
class OffenceAdmin(admin.ModelAdmin):
    filter_horizontal = ('alleged_offences',)




class SectionRegulationForm(forms.ModelForm):
    offence_text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = models.SectionRegulation
        fields = '__all__'


class SectionRegulationAdmin(VersionAdmin):
    form = SectionRegulationForm


admin.site.register(models.SectionRegulation, SectionRegulationAdmin)

