from django.contrib import admin
from django import forms

from reversion.admin import VersionAdmin

from wildlifelicensing.apps.main.models import WildlifeLicenceType, Condition, DefaultCondition
from wildlifelicensing.apps.main.forms import BetterJSONField


class DefaultConditionInline(admin.TabularInline):
    model = DefaultCondition
    ordering = ('order',)


class WildlifeLicenceTypeAdminForm(forms.ModelForm):
    application_schema = BetterJSONField()

    class Meta:
        model = WildlifeLicenceType
        exclude = []


# Register your models here.
@admin.register(WildlifeLicenceType)
class WildlifeLicenceTypeAdmin(VersionAdmin):
    list_display = ('name', 'display_name', 'code')
    prepopulated_fields = {'code_slug': ('code', 'version')}
    filter_horizontal = ('default_conditions',)
    inlines = (DefaultConditionInline,)
    form = WildlifeLicenceTypeAdminForm


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
