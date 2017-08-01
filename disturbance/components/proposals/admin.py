from django.contrib import admin
from ledger.accounts.models import EmailUser
from disturbance.components.proposals import models
from disturbance.components.proposals import forms 
from reversion.admin import VersionAdmin
# Register your models here.

@admin.register(models.ProposalType)
class ProposalTypeAdmin(admin.ModelAdmin):
    exclude=("site",) 

class ProposalDocumentInline(admin.TabularInline):
    model = models.ProposalDocument
    extra = 0

@admin.register(models.Proposal)
class ProposalAdmin(VersionAdmin):
    inlines =[ProposalDocumentInline,] 

@admin.register(models.ProposalAssessorGroup)
class ProposalAssessorGroupAdmin(admin.ModelAdmin):
    list_display = ['name','default']
    filter_horizontal = ('members',)
    form = forms.ProposalAssessorGroupAdminForm
    readonly_fields = ['default']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.default:
            return False
        return super(ProposalAssessorGroupAdmin, self).has_delete_permission(request, obj)

@admin.register(models.ProposalApproverGroup)
class ProposalApproverGroupAdmin(admin.ModelAdmin):
    list_display = ['name','default']
    filter_horizontal = ('members',)
    form = forms.ProposalApproverGroupAdminForm
    readonly_fields = ['default']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.default:
            return False
        return super(ProposalApproverGroupAdmin, self).has_delete_permission(request, obj)

@admin.register(models.ProposalStandardRequirement)
class ProposalStandardRequirementAdmin(admin.ModelAdmin):
    list_display = ['code','text','obsolete']
