from django.contrib import admin
from commercialoperator.components.compliances import models
# Register your models here.

#@admin.register(models.ComplianceAmendmentInfo)
#class ComplianceAmendmentInfoAdmin(admin.ModelAdmin):
#    list_display = ['status']

#@admin.register(models.ComplianceAmendmentStatus)
#class ComplianceAmendmentStatusAdmin(admin.ModelAdmin):
#    list_display = ['status']

@admin.register(models.ComplianceAmendmentReason)
class ComplianceAmendmentReasonAdmin(admin.ModelAdmin):
    list_display = ['reason']

