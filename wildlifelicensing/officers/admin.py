from django.contrib import admin
from django.contrib.auth.admin import Group, GroupAdmin


from customers.models import Customer
from wildlifelicensing.admin import admin_site


@admin.register(Customer, site=admin_site)
class CustomerAdmin(admin.ModelAdmin):
    ordering = ('email', 'first_name', 'last_name')
    search_fields = ('email', 'first_name', 'last_name')
    list_display = ('email', 'first_name', 'last_name')

