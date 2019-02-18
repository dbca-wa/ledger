from django.contrib import messages
from django.contrib.gis import admin
from mooring import models

@admin.register(models.MooringsiteClass)
class MooringsiteClassAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(models.MarinePark)
class MarinaAdmin(admin.GeoModelAdmin):
    list_display = ('name','district')
    ordering = ('name',)
    list_filter = ('district',)
    search_fields = ('name',)
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    exclude = ('ratis_id',)

@admin.register(models.MooringArea)
class MooringAreaAdmin(admin.GeoModelAdmin):
    list_display = ('name','park','promo_area','mooring_type','max_advance_booking')
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('mooring_type','site_type')
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'

@admin.register(models.MooringAreaGroup)
class MooringAreaGroupAdmin(admin.ModelAdmin):
    filter_horizontal = ('members','moorings')

@admin.register(models.Mooringsite)
class MooringsiteAdmin(admin.GeoModelAdmin):
    list_display = ('name','mooringarea',)
    ordering = ('name',)
    list_filter = ('mooringarea',)
    search_fields = ('name',)
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'

@admin.register(models.Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name','description')
    ordering = ('name',)
    search_fields = ('name',)

class BookingInvoiceInline(admin.TabularInline):
    model = models.BookingInvoice
    extra = 0

class MooringsiteBookingInline(admin.TabularInline):
    model = models.MooringsiteBooking
    extra = 0

@admin.register(models.Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('arrival','departure','mooringarea','legacy_id','legacy_name','cost_total')
    ordering = ('-arrival',)
    search_fileds = ('arrival','departure')
    list_filter = ('arrival','departure','mooringarea')
    inlines = [BookingInvoiceInline,MooringsiteBookingInline]

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(models.MooringsiteBooking)
class MooringsiteBookingAdmin(admin.ModelAdmin):
    list_display = ('campsite','date','booking','booking_type')
    ordering = ('-date',)
    search_fields = ('date',)
    list_filter = ('campsite','booking_type')

@admin.register(models.MooringsiteRate)
class MooringsiteRateAdmin(admin.ModelAdmin):
    list_display = ('campsite','rate','allow_public_holidays')
    list_filter = ('campsite','rate','allow_public_holidays')
    search_fields = ('campground__name',)

@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name','phone_number')
    search_fields = ('name','phone_number')

class ReasonAdmin(admin.ModelAdmin):
    list_display = ('code','text','editable')
    search_fields = ('code','text')
    readonly_fields = ('code',)

    def get_readonly_fields(self, request, obj=None):
        fields = list(self.readonly_fields)
        if obj and not obj.editable:
            fields += ['text','editable']
        elif not obj:
            fields = []
        return fields

    def has_add_permission(self, request, obj=None):
        if obj and not obj.editable:
            return False
        return super(ReasonAdmin, self).has_delete_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and not obj.editable:
            return False
        return super(ReasonAdmin, self).has_delete_permission(request, obj)

@admin.register(models.MaximumStayReason)
class MaximumStayReason(ReasonAdmin):
    pass

@admin.register(models.PriceReason)
class PriceReason(ReasonAdmin):
    pass

@admin.register(models.ClosureReason)
class ClosureReason(ReasonAdmin):
    pass

@admin.register(models.OpenReason)
class OpenReason(ReasonAdmin):
    pass

@admin.register(models.OutstandingBookingRecipient)
class OutstandingBookingRecipient(admin.ModelAdmin):
    pass

@admin.register(models.Region)
class Region(admin.GeoModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
#    list_filter = ('mooring_type','site_type')
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    exclude = ('ratis_id',)

@admin.register(models.District)
class District(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    exclude = ('ratis_id',)
    search_fields = ('name',)
@admin.register(models.PromoArea)
class PromoArea(admin.GeoModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
    search_fields = ('name',)



admin.site.register(models.Rate)
#admin.site.register(models.Region)
#admin.site.register(models.District)
#admin.site.register(models.PromoArea)



