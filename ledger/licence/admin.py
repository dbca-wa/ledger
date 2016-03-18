from django.contrib import admin
from ledger.licence.models import LicenceType, Licence


@admin.register(LicenceType)
class LicenceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'creator', 'modifier')


@admin.register(Licence)
class LicenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'licence_type', 'status')
