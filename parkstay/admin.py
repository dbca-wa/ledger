from django.contrib import admin
from .models import Park, Campground, Campsite, CampgroundFeature, District, Region, CampsiteClass, CampsiteBooking, Booking,PromoArea, CampsiteRate

@admin.register(CampsiteClass)
class CampsiteClassAdmin(admin.ModelAdmin):
    list_display = ('name','tents','parking_spaces','allow_campervan','allow_trailer','allow_generator')
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('allow_campervan','allow_trailer','allow_generator')

@admin.register(Park)
class ParkAdmin(admin.ModelAdmin):
    list_display = ('name','district')
    ordering = ('name',)
    list_filter = ('district',)
    search_fields = ('name',)

@admin.register(Campground)
class CampgroundAdmin(admin.ModelAdmin):
    list_display = ('name','park','promo_area','campground_type','site_type','fees','is_published')
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('campground_type','site_type','is_published')

@admin.register(Campsite)
class CampsiteAdmin(admin.ModelAdmin):
    list_display = ('name','campground','campsite_class','max_people')
    ordering = ('name',)
    list_filter = ('campground','campsite_class')
    search_fields = ('name',)

@admin.register(CampgroundFeature)
class CampgroundfeatureAdmin(admin.ModelAdmin):
    list_display = ('name','description')
    ordering = ('name',)
    search_fields = ('name',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('arrival','departure','campground','legacy_id','legacy_name','cost_total')
    ordering = ('-arrival',)
    search_fileds = ('arrival','departure')
    list_filter = ('arrival','departure')

@admin.register(CampsiteBooking)
class CampsiteBookingAdmin(admin.ModelAdmin):
    list_display = ('campsite','date','booking','booking_type')
    ordering = ('-date',)
    search_fields = ('date',)
    list_filter = ('campsite','booking_type')

@admin.register(CampsiteRate)
class CampsiteRateAdmin(admin.ModelAdmin):
    list_display = ('campground','campsite_class','min_days','max_days','min_people','max_people','allow_public_holidays','rate_adult','rate_concession','rate_child','rate_infant')
    list_filter = ('campground','campsite_class','allow_public_holidays')
    search_fields = ('campground__name',)

admin.site.register(Region)
admin.site.register(District)
admin.site.register(PromoArea)

