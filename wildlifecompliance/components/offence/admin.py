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

admin.site.register(models.SectionRegulation, VersionAdmin)

