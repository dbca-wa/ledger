from django.contrib import admin
from ledger.accounts.models import EmailUser
from commercialoperator.components.organisations import models
from django.contrib.admin import actions
# Register your models here.

@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ['organisation','admin_pin_one', 'admin_pin_two', 'user_pin_one', 'user_pin_two']
    search_fields = ('organisation__name','admin_pin_one', 'admin_pin_two', 'user_pin_one', 'user_pin_two' )

@admin.register(models.OrganisationRequest)
class OrganisationRequestAdmin(admin.ModelAdmin):
    list_display = ['name','requester', 'abn', 'status']

@admin.register(models.OrganisationAccessGroup)
class OrganisationAccessGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members',)
    exclude = ('site',)
    actions = None

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "members":
            #kwargs["queryset"] = EmailUser.objects.filter(email__icontains='@dbca.wa.gov.au')
            kwargs["queryset"] = EmailUser.objects.filter(is_staff=True)
        return super(OrganisationAccessGroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def has_add_permission(self, request):
        return True if models.OrganisationAccessGroup.objects.count() == 0 else False

    def has_delete_permission(self, request, obj=None):
        return False 

