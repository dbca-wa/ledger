from django.contrib import admin
from oscar.apps.order.admin import *  # noqa
from oscar.core.loading import get_model

Order = get_model('order', 'Order')

admin.site.unregister(Order)
class OrderAdmin(OrderAdmin):
    raw_id_fields = ['user', 'billing_address', 'shipping_address', 'basket']
    list_display = ('number', 'total_incl_tax', 'site', 'user',
                    'billing_address', 'date_placed')
    readonly_fields = ('number', 'total_incl_tax', 'total_excl_tax',
                       'shipping_incl_tax', 'shipping_excl_tax',)
    inlines = [LineInline]
    search_fields = ('number','user__email',)
admin.site.register(Order, OrderAdmin)
