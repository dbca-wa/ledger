from django.contrib import admin
from disturbance import models
# Register your models here.

@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    pass

@admin.register(models.OrganisationRequest)
class OrganisationRequestAdmin(admin.ModelAdmin):
    pass

@admin.register(models.ProposalType)
class ProposalTypeAdmin(admin.ModelAdmin):
    exclude=("site",) 
