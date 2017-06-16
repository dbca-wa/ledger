from django.contrib import admin
from disturbance.components.proposals import models
# Register your models here.

@admin.register(models.ProposalType)
class ProposalTypeAdmin(admin.ModelAdmin):
    exclude=("site",) 

@admin.register(models.Proposal)
class ProposalAdmin(admin.ModelAdmin):
    pass
