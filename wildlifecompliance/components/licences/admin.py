from django.contrib import admin
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.licences import models
# Register your models here.

@admin.register(models.WildlifeLicenceCategory)
class WildlifeLicenceCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(models.WildlifeLicenceActivityType)
class WildlifeLicenceActivityTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(models.DefaultActivityType)
class DefaultActivityTypeAdmin(admin.ModelAdmin):
    pass