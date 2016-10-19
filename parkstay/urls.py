from django.conf.urls import url, include
from rest_framework import routers
from parkstay import views
from parkstay.admin import admin

from ledger.urls import urlpatterns as ledger_patterns

# API patterns
router = routers.DefaultRouter()
router.register(r'campgrounds', views.CampgroundViewSet)
#router.register(r'campsites', views.CampsiteViewSet)
router.register(r'campsite_bookings', views.CampsiteBookingViewSet)
router.register(r'promo_areas',views.PromoAreaViewSet)
router.register(r'parks',views.ParkViewSet)
router.register(r'campground_feature',views.FeatureViewSet)
router.register(r'regions',views.RegionViewSet)
#router.register(r'campsite_classes',views.CampsiteClassViewSet)
router.register(r'booking',views.BookingViewSet)
router.register(r'campsite_rate',views.CampsiteRateViewSet)

api_patterns = [
    url(r'^api/campsites/$', views.get_campsite_bookings, name='get_campsite_bookings'),
    url(r'^api/campsite_classes/$', views.get_campsite_class_bookings, name='get_campsite_class_bookings'),
    url(r'api/',include(router.urls))
]

# URL Patterns
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include(api_patterns)),
    url(r'^campsites/(?P<ground_id>[0-9]+)/$', views.CampsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    url(r'^campsite_classes/(?P<ground_id>[0-9]+)/$', views.CampsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    url(r'^ical/campground/(?P<ground_id>[0-9]+)/$', views.CampgroundFeed(), name='campground_calendar'),

] + ledger_patterns

