from django.contrib import admin
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.call_email import models
# Register your models here.


@admin.register(models.Classification)
class ClassificationAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    pass

@admin.register(models.SpeciesType)
class SpeciesTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Referrer)
class ReferrerAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    pass

