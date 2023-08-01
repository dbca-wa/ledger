from django.contrib import messages
from django.contrib.gis import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from django.db.models import Q

from ledger.accounts import admin as ledger_admin
from ledger.accounts.models import EmailUser
from copy import deepcopy
from ledgergw import models
from django.contrib.admin import ModelAdmin

admin.site.unregister(EmailUser)
@admin.register(EmailUser)
class EmailUserAdmin(ledger_admin.EmailUserAdmin):
    """
    Override the EmailUserAdmin from ledger.accounts.admin to remove is_superuser checkbox field on Admin page
    """
    def get_fieldsets(self, request, obj=None):
        """ Remove the is_superuser checkbox from the Admin page, is user is Mooring Admin or RIA Admin and NOT superuser."""
        fieldsets = super(UserAdmin, self).get_fieldsets(request, obj)
        if not obj:
            return fieldsets
        
        if request.user.is_superuser:
            return fieldsets

        group = Group.objects.filter(name='Mooring Admin')
        if group and (group[0] in request.user.groups.all()):
            fieldsets = deepcopy(fieldsets)
            for fieldset in fieldsets:
                if 'is_superuser' in fieldset[1]['fields']:
                    if type(fieldset[1]['fields']) == tuple:
                        fieldset[1]['fields'] = list(fieldset[1]['fields'])
                    fieldset[1]['fields'].remove('is_superuser')
                    break
        return fieldsets


@admin.register(models.API)
class APIAdmin(ModelAdmin):
     list_display = ('id','system_name','system_id','active')


@admin.register(models.JobQueue)
class JobQueueAdmin(ModelAdmin):
     list_display = ('id','job_cmd','parameters_json','system_id','status','processed_dt','user','created')
     search_fields = ('job_cmd','parameters_json',)
     list_filter = ('system_id','created')  
     ordering = ('id',)


