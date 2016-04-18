from django.contrib import admin

from reversion.admin import VersionAdmin

from wildlifelicensing.apps.main.models import WildlifeLicenceType, Condition


# Register your models here.
@admin.register(WildlifeLicenceType)
class LicenceTypeAdmin(VersionAdmin):
    list_display = ('name', 'code')
    filter_horizontal = ('default_conditions',)


# Register your models here.
@admin.register(Condition)
class ConditionAdmin(VersionAdmin):
    pass
