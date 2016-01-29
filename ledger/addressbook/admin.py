from django.contrib import admin
from addressbook.models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass
