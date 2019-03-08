from django.contrib import admin
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.call_email import models
# Register your models here.


@admin.register(models.Classification)
class ClassificationAdmin(admin.ModelAdmin):
    pass



