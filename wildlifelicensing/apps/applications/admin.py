from django.contrib import admin
from django import forms
from reversion.admin import VersionAdmin

from wildlifelicensing.apps.main.models import AssessorGroup
from wildlifelicensing.apps.main.forms import BetterJSONField

from wildlifelicensing.apps.applications.models import Application, ApplicationCondition


class ApplicationAdminForm(forms.ModelForm):
    data = BetterJSONField()

    class Meta:
        model = Application
        exclude = []

class ApplicationConditionInline(admin.TabularInline):
    model = ApplicationCondition
    extra = 1
    ordering = ('order',)

@admin.register(Application)
class ApplicationAdmin(VersionAdmin):
    date_hierarchy = 'lodgement_date'
    list_display = ('licence_type', 'get_user', 'processing_status', 'lodgement_number', 'lodgement_date')
    form = ApplicationAdminForm
    inlines = [ApplicationConditionInline,]

    def get_user(self, obj):
        return obj.applicant

    get_user.short_description = 'User'
    get_user.admin_order_field = 'applicant_profile__user'


@admin.register(AssessorGroup)
class AssessorGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(AssessorGroupAdmin, self).get_form(request, obj, **kwargs)

        # only users in Assessors group can be in an Assessor Group
        form.base_fields['members'].queryset = form.base_fields['members'].queryset.filter(groups__name='Assessors')

        return form
