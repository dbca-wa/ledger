from django.contrib import admin
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.call_email import models
# Register your models here.


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    pass

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
