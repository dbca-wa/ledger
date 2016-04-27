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
    list_display = ['code', 'text']
    search_fields = ['code', 'text']
    ordering = ['code']
    actions = ['make_obsolete']

    def get_actions(self, request):
        actions = super(ConditionAdmin, self).get_actions(request)

        if 'delete_selected' in actions:
            del actions['delete_selected']

        return actions

    def make_obsolete(self, request, queryset):
            queryset.update(obsolete=True)

    def has_delete_permission(self, request, obj=None):
        return False

    make_obsolete.short_description = 'Mark selected conditions as obsolete'
