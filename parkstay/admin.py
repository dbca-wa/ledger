from django.contrib import admin
from .models import Park, Campground, Campsite, CampgroundFeature, Region, CampsiteClass, CampsiteBooking, Booking,PromoArea

@admin.register(CampsiteClass)
class CampsiteClassAdmin(admin.ModelAdmin):
    ordering = ('name',)

admin.site.register(Park)
admin.site.register(Campground)
admin.site.register(Campsite)
admin.site.register(CampgroundFeature)
admin.site.register(Region)
admin.site.register(CampsiteBooking)
admin.site.register(Booking)
admin.site.register(PromoArea)

