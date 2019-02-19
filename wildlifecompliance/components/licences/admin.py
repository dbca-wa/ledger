from django.contrib import admin
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.licences import models
# Register your models here.


@admin.register(models.WildlifeLicenceClass)
class WildlifeLicenceClassAdmin(admin.ModelAdmin):
    pass


@admin.register(models.WildlifeLicenceActivityType)
class WildlifeLicenceActivityTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.WildlifeLicence)
class WildlifeLicence(admin.ModelAdmin):
    pass


@admin.register(models.DefaultActivityType)
class DefaultActivityTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.WildlifeLicenceActivity)
class WildlifeLicenceActivitydmin(admin.ModelAdmin):
    pass


@admin.register(models.DefaultActivity)
class DefaultActivityAdmin(admin.ModelAdmin):
    pass
