from django.contrib import admin
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.applications import models
from wildlifecompliance.components.applications import forms 
from reversion.admin import VersionAdmin


class ApplicationDocumentInline(admin.TabularInline):
    model = models.ApplicationDocument
    extra = 0

@admin.register(models.AmendmentRequest)
class AmendmentRequestAdmin(admin.ModelAdmin):
    list_display = ['application','licence_activity_type']

@admin.register(models.ApplicationDecisionPropose)
class ApplicationDecisionPropose(admin.ModelAdmin):
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
    list_display = ['name','display_name']
    filter_horizontal = ('members',)
    form = forms.ApplicationGroupTypeAdminForm

    def has_delete_permission(self, request, obj=None):
        return super(ApplicationGroupTypeAdmin, self).has_delete_permission(request, obj)

class ApplicationInvoiceInline(admin.TabularInline):
    model = models.ApplicationInvoice
    extra = 0

@admin.register(models.Application)
class ApplicationAdmin(VersionAdmin):
    inlines =[ApplicationDocumentInline,ApplicationInvoiceInline]

@admin.register(models.ApplicationAssessorGroup)
class ApplicationAssessorGroupAdmin(admin.ModelAdmin):
    list_display = ['name','default']
    filter_horizontal = ('members',)
    form = forms.ApplicationAssessorGroupAdminForm
    readonly_fields = ['default']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.default:
            return False
        return super(ApplicationAssessorGroupAdmin, self).has_delete_permission(request, obj)

@admin.register(models.ApplicationApproverGroup)
class ApplicationApproverGroupAdmin(admin.ModelAdmin):
    list_display = ['name','default']
    filter_horizontal = ('members',)
    form = forms.ApplicationApproverGroupAdminForm
    readonly_fields = ['default']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.default:
            return False
        return super(ApplicationApproverGroupAdmin, self).has_delete_permission(request, obj)

@admin.register(models.ApplicationStandardCondition)
class ApplicationStandardConditionAdmin(admin.ModelAdmin):
    list_display = ['code','text','obsolete']
