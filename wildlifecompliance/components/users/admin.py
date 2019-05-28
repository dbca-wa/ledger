from django.contrib import admin
from wildlifecompliance.components.users import models
from wildlifecompliance.components.users import forms
from reversion.admin import VersionAdmin

@admin.register(models.CompliancePermissionGroup)
class CompliancePermissionGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name']
    filter_horizontal = ('region_district',)
    form = forms.CompliancePermissionGroupAdminForm

    def has_delete_permission(self, request, obj=None):
        return super(
            CompliancePermissionGroupAdmin,
            self).has_delete_permission(
            request,
            obj)
