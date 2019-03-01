from django.contrib import admin
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.licences import models
# Register your models here.


@admin.register(models.LicenceCategory)
class LicenceCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(models.LicenceActivity)
class LicenceActivityAdmin(admin.ModelAdmin):
    pass


@admin.register(models.WildlifeLicence)
class WildlifeLicence(admin.ModelAdmin):
    pass


@admin.register(models.DefaultActivity)
class DefaultActivityAdmin(admin.ModelAdmin):
    pass


@admin.register(models.LicencePurpose)
class LicencePurposeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.DefaultPurpose)
class DefaultPurposeAdmin(admin.ModelAdmin):
    pass
