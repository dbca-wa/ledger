from django.contrib import admin

from reversion.admin import VersionAdmin

from wildlifelicensing.apps.main.models import WildlifeLicenceType, Condition, DefaultCondition


class DefaultConditionInline(admin.TabularInline):
    model = DefaultCondition
    ordering = ('order',)


# Register your models here.
@admin.register(WildlifeLicenceType)
class WildlifeLicenceTypeAdmin(VersionAdmin):
    list_display = ('name', 'code')
    filter_horizontal = ('default_conditions',)
    inlines = (DefaultConditionInline,)


# Register your models here.
@admin.register(Condition)
class ConditionAdmin(VersionAdmin):
    pass
