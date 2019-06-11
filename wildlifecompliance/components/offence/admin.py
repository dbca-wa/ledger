from django.contrib import admin

from wildlifecompliance.components.offence import models


# class SectionRegulationInline(admin.TabularInline):
#     model = models.SectionRegulation
#     extra = 10


@admin.register(models.Offence)
class OffenceAdmin(admin.ModelAdmin):
    # inlines = (SectionRegulationInline,)
    pass


@admin.register(models.Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    pass


@admin.register(models.SectionRegulation)
class SectionRegulationAdmin(admin.ModelAdmin):
    pass


