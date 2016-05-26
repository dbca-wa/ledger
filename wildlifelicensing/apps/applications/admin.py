from django.contrib import admin

from reversion.admin import VersionAdmin

from wildlifelicensing.apps.main.models import AssessorGroup

from models import Application


@admin.register(Application)
class ApplicationAdmin(VersionAdmin):
    date_hierarchy = 'lodgement_date'
    list_display = ('licence_type', 'get_user', 'processing_status', 'lodgement_number', 'lodgement_date')

    def get_user(self, obj):
        return obj.applicant_profile.user
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
