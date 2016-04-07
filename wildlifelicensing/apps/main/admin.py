from django.contrib import admin

from reversion.admin import VersionAdmin

from wildlifelicensing.apps.main.models import WildlifeLicenceType


# Register your models here.
@admin.register(WildlifeLicenceType)
class LicenceTypeAdmin(VersionAdmin):
    list_display = ('name', 'code')
