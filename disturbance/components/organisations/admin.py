from django.contrib import admin
from disturbance.components.organisations import models
# Register your models here.

@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    pass

@admin.register(models.OrganisationRequest)
class OrganisationRequestAdmin(admin.ModelAdmin):
    pass

