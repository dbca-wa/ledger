from django.contrib import admin
from ledger.accounts.models import EmailUser
from disturbance.components.proposals import models
from disturbance.components.proposals import forms
from disturbance.components.main.models import ActivityMatrix, SystemMaintenance, ApplicationType, GlobalSettings
#from disturbance.components.main.models import Activity, SubActivityLevel1, SubActivityLevel2, SubCategory
from reversion.admin import VersionAdmin
from django.conf.urls import url
from django.template.response import TemplateResponse
from django.http import HttpResponse, HttpResponseRedirect
from disturbance.utils import create_helppage_object
# Register your models here.

@admin.register(models.ProposalType)
class ProposalTypeAdmin(admin.ModelAdmin):
    list_display = ['name','description', 'version']
    ordering = ('name', '-version')
    list_filter = ('name',)
    #exclude=("site",)

class ProposalDocumentInline(admin.TabularInline):
    model = models.ProposalDocument
    extra = 0

@admin.register(models.AmendmentReason)
class AmendmentReasonAdmin(admin.ModelAdmin):
    list_display = ['reason']

@admin.register(models.Proposal)
class ProposalAdmin(VersionAdmin):
    inlines =[ProposalDocumentInline,]

@admin.register(models.ProposalAssessorGroup)
class ProposalAssessorGroupAdmin(admin.ModelAdmin):
    list_display = ['name','default']
    filter_horizontal = ('members',)
    form = forms.ProposalAssessorGroupAdminForm
    readonly_fields = ['default']
    #readonly_fields = ['regions', 'activities']

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
    #readonly_fields = ['default', 'regions', 'activities']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.default:
            return False
        return super(ProposalApproverGroupAdmin, self).has_delete_permission(request, obj)

@admin.register(models.ProposalStandardRequirement)
class ProposalStandardRequirementAdmin(admin.ModelAdmin):
    list_display = ['code','text','obsolete']


@admin.register(models.HelpPage)
class HelpPageAdmin(admin.ModelAdmin):
    list_display = ['application_type','help_type', 'description', 'version']
    form = forms.DisturbanceHelpPageAdminForm
    change_list_template = "disturbance/help_page_changelist.html"
    ordering = ('application_type', 'help_type', '-version')
    list_filter = ('application_type', 'help_type')


    def get_urls(self):
        urls = super(HelpPageAdmin, self).get_urls()
        my_urls = [
            url('create_disturbance_help/', self.admin_site.admin_view(self.create_disturbance_help)),
            url('create_apiary_help/', self.admin_site.admin_view(self.create_apiary_help)),
            url('create_disturbance_help_assessor/', self.admin_site.admin_view(self.create_disturbance_help_assessor)),
            url('create_apiary_help_assessor/', self.admin_site.admin_view(self.create_apiary_help_assessor)),
        ]
        return my_urls + urls

    def create_disturbance_help(self, request):
        create_helppage_object(application_type='Disturbance', help_type=models.HelpPage.HELP_TEXT_EXTERNAL)
        return HttpResponseRedirect("../")

    def create_apiary_help(self, request):
        create_helppage_object(application_type='Apiary', help_type=models.HelpPage.HELP_TEXT_EXTERNAL)
        return HttpResponseRedirect("../")

    def create_disturbance_help_assessor(self, request):
        create_helppage_object(application_type='Disturbance', help_type=models.HelpPage.HELP_TEXT_INTERNAL)
        return HttpResponseRedirect("../")

    def create_apiary_help_assessor(self, request):
        create_helppage_object(application_type='Apiary', help_type=models.HelpPage.HELP_TEXT_INTERNAL)
        return HttpResponseRedirect("../")

@admin.register(ActivityMatrix)
class ActivityMatrixAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'version']
    ordering = ('name', '-version')


@admin.register(SystemMaintenance)
class SystemMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'start_date', 'end_date', 'duration']
    ordering = ('start_date',)
    readonly_fields = ('duration',)
    form = forms.SystemMaintenanceAdminForm

@admin.register(ApplicationType)
class ApplicationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'visible']
    ordering = ('order',)

@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']
    ordering = ('key',)
