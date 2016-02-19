from django.contrib import admin
from wildlife_licence.models import CustomerRole, WildlifeLicenceType,  WildlifeLicence


@admin.register(CustomerRole)
class CustomerRoleAdmin(admin.ModelAdmin):
    list_diplay = ('user', 'organisation_name')


@admin.register(WildlifeLicenceType)
class WildlifeLicenceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'creator', 'modifier')


@admin.register(WildlifeLicence)
class WildlifeLicenceAdmin(admin.ModelAdmin):
    list_display = ('customer_role', 'licence_type', 'status')
