from django.contrib import admin
from wildlifecompliance.components.applications import models
from wildlifecompliance.components.applications import forms
from reversion.admin import VersionAdmin


class ApplicationDocumentInline(admin.TabularInline):
    model = models.ApplicationDocument
    extra = 0


@admin.register(models.AmendmentRequest)
class AmendmentRequestAdmin(admin.ModelAdmin):
    list_display = ['application', 'licence_activity']


@admin.register(models.ApplicationSelectedActivity)
class ApplicationSelectedActivity(admin.ModelAdmin):
    pass


@admin.register(models.Assessment)
class Assessment(admin.ModelAdmin):
    pass


@admin.register(models.ApplicationCondition)
class ApplicationCondition(admin.ModelAdmin):
    pass


@admin.register(models.DefaultCondition)
class DefaultCondition(admin.ModelAdmin):
    pass


@admin.register(models.ApplicationGroupType)
class ApplicationGroupTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name']
    filter_horizontal = ('members',)
    form = forms.ApplicationGroupTypeAdminForm

    def has_delete_permission(self, request, obj=None):
        return super(
            ApplicationGroupTypeAdmin,
            self).has_delete_permission(
            request,
            obj)


class ApplicationInvoiceInline(admin.TabularInline):
    model = models.ApplicationInvoice
    extra = 0


@admin.register(models.Application)
class ApplicationAdmin(VersionAdmin):
    inlines = [ApplicationDocumentInline, ApplicationInvoiceInline]


@admin.register(models.ApplicationStandardCondition)
class ApplicationStandardConditionAdmin(admin.ModelAdmin):
    list_display = ['code', 'text', 'obsolete']
