from django.contrib import admin

from reversion.admin import VersionAdmin

from ledger.licence.models import LicenceType, Licence


@admin.register(LicenceType)
class LicenceTypeAdmin(VersionAdmin):
    list_display = ('name', 'code')


@admin.register(Licence)
class LicenceAdmin(VersionAdmin):
    list_display = ('user', 'licence_type', 'status')
