from django.contrib import admin
from wildlifecompliance.components.organisations import models
# Register your models here.


@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.OrganisationRequest)
class OrganisationRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(models.OrganisationContact)
class OrganisationContactAdmin(admin.ModelAdmin):
    pass


@admin.register(models.UserDelegation)
class UserDelegationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.OrganisationAction)
class UOrganisationActionAdmin(admin.ModelAdmin):
    pass
