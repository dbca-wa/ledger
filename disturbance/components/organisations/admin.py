from django.contrib import admin
from disturbance.components.organisations import models
# Register your models here.

@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    pass

@admin.register(models.OrganisationRequest)
class OrganisationRequestAdmin(admin.ModelAdmin):
    pass

@admin.register(models.OrganisationAccessGroup)
class OrganisationAccessGroupAdmin(admin.ModelAdmin):

    exclude = ('site',)

    def has_add_permission(self, request):
        return True if models.OrganisationAccessGroup.objects.count() == 0 else False
