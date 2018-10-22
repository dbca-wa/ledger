from django.contrib import admin
from disturbance.components.compliances import models
# Register your models here.

#@admin.register(models.ComplianceAmendmentInfo)
#class ComplianceAmendmentInfoAdmin(admin.ModelAdmin):
#    list_display = ['status']

#@admin.register(models.ComplianceAmendmentStatus)
#class ComplianceAmendmentStatusAdmin(admin.ModelAdmin):
#    list_display = ['status']

@admin.register(models.AmendmentReason)
class AmendmentReasonAdmin(admin.ModelAdmin):
    list_display = ['reason']

