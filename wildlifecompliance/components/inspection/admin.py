from django.contrib import admin
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.inspection import models
from reversion.admin import VersionAdmin


@admin.register(models.Inspection)
class InspectionAdmin(admin.ModelAdmin):
    pass

@admin.register(models.InspectionType)
class InspectionTypeAdmin(admin.ModelAdmin):
    pass
