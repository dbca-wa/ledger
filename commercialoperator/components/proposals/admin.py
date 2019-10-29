from django.contrib import admin
from ledger.accounts.models import EmailUser
from commercialoperator.components.proposals import models
from commercialoperator.components.bookings.models import ApplicationFeeInvoice
from commercialoperator.components.proposals import forms
from commercialoperator.components.main.models import (
    ActivityMatrix,
    SystemMaintenance,
    ApplicationType,
    Park,
    #ParkPrice,
    Trail,
    ActivityType,
    ActivityCategory,
    Activity,
    AccessType,
    Section,
    Zone,
    RequiredDocument,
    Question,
    GlobalSettings
)
#from commercialoperator.components.main.models import Activity, SubActivityLevel1, SubActivityLevel2, SubCategory
from reversion.admin import VersionAdmin
from django.conf.urls import url
from django.template.response import TemplateResponse
from django.http import HttpResponse, HttpResponseRedirect
from commercialoperator.utils import create_helppage_object
# Register your models here.

# Commented since COLS does not use schema - so will not require direct editing by user in Admin (although a ProposalType is still required for ApplicationType)
#@admin.register(models.ProposalType)
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

    def get_actions(self, request):
        actions =  super(ProposalAssessorGroupAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        if self.model.objects.count() == 1:
            return False
        return super(ProposalAssessorGroupAdmin, self).has_delete_permission(request, obj)

    def has_add_permission(self, request):
        if self.model.objects.count() > 0:
            return False
        return super(ProposalAssessorGroupAdmin, self).has_add_permission(request)


@admin.register(models.ProposalApproverGroup)
class ProposalApproverGroupAdmin(admin.ModelAdmin):
    list_display = ['name','default']
    filter_horizontal = ('members',)
    form = forms.ProposalApproverGroupAdminForm
    readonly_fields = ['default']
    #readonly_fields = ['default', 'regions', 'activities']

    def get_actions(self, request):
        actions =  super(ProposalApproverGroupAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        if self.model.objects.count() == 1:
            return False
        return super(ProposalApproverGroupAdmin, self).has_delete_permission(request, obj)

    def has_add_permission(self, request):
        if self.model.objects.count() > 0:
            return False
        return super(ProposalApproverGroupAdmin, self).has_add_permission(request)

@admin.register(models.ProposalStandardRequirement)
class ProposalStandardRequirementAdmin(admin.ModelAdmin):
    list_display = ['code','text','obsolete']

#@admin.register(models.HelpPage)
class HelpPageAdmin(admin.ModelAdmin):
    list_display = ['application_type','help_type', 'description', 'version']
    form = forms.CommercialOperatorHelpPageAdminForm
    change_list_template = "commercialoperator/help_page_changelist.html"
    ordering = ('application_type', 'help_type', '-version')
    list_filter = ('application_type', 'help_type')


    def get_urls(self):
        urls = super(HelpPageAdmin, self).get_urls()
        my_urls = [
            url('create_commercialoperator_help/', self.admin_site.admin_view(self.create_commercialoperator_help)),
            url('create_commercialoperator_help_assessor/', self.admin_site.admin_view(self.create_commercialoperator_help_assessor)),
        ]
        return my_urls + urls

    def create_commercialoperator_help(self, request):
        create_helppage_object(application_type='T Class', help_type=models.HelpPage.HELP_TEXT_EXTERNAL)
        return HttpResponseRedirect("../")

    def create_commercialoperator_help_assessor(self, request):
        create_helppage_object(application_type='T Class', help_type=models.HelpPage.HELP_TEXT_INTERNAL)
        return HttpResponseRedirect("../")

@admin.register(models.ChecklistQuestion)
class ChecklistQuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'list_type', 'obsolete','answer_type']
    ordering = ('list_type',)

@admin.register(SystemMaintenance)
class SystemMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'start_date', 'end_date', 'duration']
    ordering = ('start_date',)
    readonly_fields = ('duration',)
    form = forms.SystemMaintenanceAdminForm

@admin.register(ApplicationType)
class ApplicationTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'visible', 'max_renewals', 'max_renewal_period', 'application_fee']
    ordering = ('order',)

@admin.register(Park)
class ParkAdmin(admin.ModelAdmin):
    list_display = ['name', 'district']
    #filter_horizontal = ('allowed_activities',)
    filter_horizontal = ('allowed_activities', 'allowed_access')
    ordering = ('name',)

@admin.register(Trail)
class TrailAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    filter_horizontal = ('allowed_activities',)
    ordering = ('name',)

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'visible', 'trail', 'doc_url']
    ordering = ('name',)

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'visible', 'park']
    filter_horizontal = ('allowed_activities',)
    ordering = ('name',)

@admin.register(models.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['access_type','capacity', 'rego', 'license', 'rego_expiry']
    ordering = ('access_type',)

@admin.register(models.Vessel)
class VesselAdmin(admin.ModelAdmin):
    list_display = ['nominated_vessel','spv_no', 'hire_rego', 'craft_no', 'size', 'proposal']
    ordering = ('nominated_vessel',)

@admin.register(RequiredDocument)
class RequiredDocumentAdmin(admin.ModelAdmin):
    list_display = ['park', 'activity', 'question']
    #filter_horizontal = ('allowed_activities',)
    #ordering = ('name',)

@admin.register(ActivityCategory)
class ActivityCategory(admin.ModelAdmin):
    list_display = ['name', 'visible', 'activity_type']
    ordering = ('name',)

@admin.register(Activity)
class Activity(admin.ModelAdmin):
    list_display = ['name', 'visible', 'activity_category']
    ordering = ('name',)

@admin.register(AccessType)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['id','name','visible']
    ordering = ('id',)

@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value']
    ordering = ('key',)

@admin.register(models.ReferralRecipientGroup)
class ReferralRecipientGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    list_display = ['name']
    exclude = ('site',)
    actions = None

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "members":
            kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        return super(ReferralRecipientGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

@admin.register(models.QAOfficerGroup)
class QAOfficerGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    list_display = ['name']
    exclude = ('site',)
    actions = None

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "members":
            #kwargs["queryset"] = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
            kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        return super(QAOfficerGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    #list_display = ['id','name', 'visible']
    list_display = ['name']
    ordering = ('id',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'answer_one', 'answer_two', 'answer_three', 'answer_four',]
    ordering = ('question_text',)

@admin.register(ApplicationFeeInvoice)
class SectionAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ApplicationFeeInvoice._meta.fields]

