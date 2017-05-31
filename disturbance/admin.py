from django.contrib import admin
from disturbance import models
# Register your models here.

@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    pass
