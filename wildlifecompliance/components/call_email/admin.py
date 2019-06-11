from django.contrib import admin
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.call_email import models
from reversion.admin import VersionAdmin



@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.MapLayer)
class MaplayerAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'layer_name', 'availability']


@admin.register(models.ReportType)
class ReportTypeAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'version', 'date_created']
    ordering = ['report_type', '-version']


@admin.register(models.Referrer)
class ReferrerAdmin(admin.ModelAdmin):
    pass


@admin.register(models.CallEmail)
class CallEmailAdmin(admin.ModelAdmin):
    pass

# @admin.register(models.CallEmailSchema)
# class CallEmailSchema(admin.ModelAdmin):
#     pass
