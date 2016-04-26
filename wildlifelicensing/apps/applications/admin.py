from django.contrib import admin

from reversion.admin import VersionAdmin

from wildlifelicensing.apps.main.models import AssessorDepartment

from models import Application


@admin.register(Application)
class ApplicationAdmin(VersionAdmin):
    date_hierarchy = 'lodgement_date'
    list_display = ('lodgement_number', 'lodgement_date')


@admin.register(AssessorDepartment)
class AssessorDepartmentAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(AssessorDepartmentAdmin, self).get_form(request, obj, **kwargs)

        # only users in Assessors group can be in an Assessor Department
        form.base_fields['members'].queryset = form.base_fields['members'].queryset.filter(groups__name='Assessors')

        return form
