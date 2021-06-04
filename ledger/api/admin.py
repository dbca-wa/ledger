from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.forms import modelform_factory
from django.conf import settings
from django.contrib.auth.models import Group

from reversion.admin import VersionAdmin

from ledger.api.models import API

@admin.register(API)
class APIAdmin(admin.ModelAdmin):
    list_display = ('id','system_name','system_id','active')
