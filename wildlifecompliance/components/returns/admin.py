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

@admin.register(models.ReturnTable)
class ReturnTable(admin.ModelAdmin):
    pass

@admin.register(models.ReturnRow)
class ReturnRow(admin.ModelAdmin):
    pass