from django.contrib import admin

from reversion.admin import VersionAdmin

from wildlifelicensing.apps.returns.models import ReturnType


@admin.register(ReturnType)
class ReturnTypeAdmin(VersionAdmin):
    list_display = ('licence_type',)
