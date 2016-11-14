from django.conf.urls import url, include
from rest_framework import routers
from parkstay import views, api
from parkstay.admin import admin

from ledger.urls import urlpatterns as ledger_patterns

# API patterns
router = routers.DefaultRouter()
router.register(r'campgrounds', api.CampgroundViewSet)
#router.register(r'campsites', views.CampsiteViewSet)
router.register(r'campsite_bookings', api.CampsiteBookingViewSet)
router.register(r'promo_areas',api.PromoAreaViewSet)
router.register(r'parks',api.ParkViewSet)
router.register(r'features',api.FeatureViewSet)
router.register(r'campground_feature',api.FeatureViewSet)
router.register(r'regions',api.RegionViewSet)
router.register(r'campsite_classes',api.CampsiteClassViewSet)
router.register(r'booking',api.BookingViewSet)
router.register(r'booking_ranges',api.CampgroundBookingRangeViewset)
router.register(r'booking_ranges',api.CampsiteBookingRangeViewset)
router.register(r'campsite_rate',api.CampsiteRateViewSet)

api_patterns = [
    url(r'api/',include(router.urls))
]

# URL Patterns
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include(api_patterns)),
    url(r'^campsites/(?P<ground_id>[0-9]+)/$', views.CampsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    url(r'^campsite_classes/(?P<ground_id>[0-9]+)/$', views.CampsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    url(r'^ical/campground/(?P<ground_id>[0-9]+)/$', views.CampgroundFeed(), name='campground_calendar'),
    url(r'^dashboard/campgrounds$', views.DashboardView.as_view(), name='dash-campgrounds'),
    url(r'^dashboard/campgrounds/(?P<ground_id>[0-9]+)$', views.DashboardView.as_view(), name='dash-campground-detail'),
    url(r'^dashboard/campgrounds/addCampground$', views.DashboardView.as_view(), name='dash-addCampground'),
] + ledger_patterns
