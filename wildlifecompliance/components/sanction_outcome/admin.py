from django.contrib import admin

from wildlifecompliance.components.sanction_outcome.models import SanctionOutcome


@admin.register(SanctionOutcome)
class SanctionOutcomeAdmin(admin.ModelAdmin):
    filter_horizontal = ('alleged_offences',)
