from django.contrib import admin
from ledger.accounts.models import EmailUser
from disturbance.components.proposals import models
from disturbance.components.proposals import forms 
# Register your models here.

@admin.register(models.ProposalType)
class ProposalTypeAdmin(admin.ModelAdmin):
    exclude=("site",) 

@admin.register(models.Proposal)
class ProposalAdmin(admin.ModelAdmin):
    pass

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
