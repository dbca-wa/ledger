from django.contrib import admin
from django.contrib.auth.admin import Group, GroupAdmin


from models import Customer
from wildlifelicensing.admin import wildlife_licensing_admin_site

from rollcall.models import EmailUser
from rollcall.admin import EmailUserAdmin

wildlife_licensing_admin_site.register(EmailUser, EmailUserAdmin)
wildlife_licensing_admin_site.register(Group, GroupAdmin)


@admin.register(Customer, site=wildlife_licensing_admin_site)
class CustomerAdmin(admin.ModelAdmin):
    ordering = ('user', 'user__first_name', 'user__last_name')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    list_display = ('user', 'first_name', 'last_name')

    def first_name(self, obj):
        return obj.user.first_name

    first_name.admin_order_field = 'user__first_name'

    def last_name(self, obj):
        return obj.user.last_name

    last_name.admin_order_field = 'user__last_name'
