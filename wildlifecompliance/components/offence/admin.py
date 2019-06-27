from django import forms
from django.contrib import admin
from reversion.admin import VersionAdmin

from wildlifecompliance.components.offence import models


@admin.register(models.Offence)
class OffenceAdmin(admin.ModelAdmin):
    filter_horizontal = ('alleged_offences',)


# @admin.register(models.Penalty)
# class PenaltyAdmin(admin.ModelAdmin):
#     pass


# @admin.register(models.SectionRegulation)
# class SectionRegulationAdmin(admin.ModelAdmin):
#     pass

class SectionRegulationForm(forms.ModelForm):
    offence_text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = models.SectionRegulation
        fields = '__all__'


class SectionRegulationAdmin(VersionAdmin):
    form = SectionRegulationForm


admin.site.register(models.SectionRegulation, SectionRegulationAdmin)

