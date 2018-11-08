from django.contrib import admin
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.returns import models
from reversion.admin import VersionAdmin
# Register your models here.

@admin.register(models.ReturnType)
class ReturnTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(models.Return)
class ReturnAdmin(admin.ModelAdmin):
    pass
