from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from parkstay import views, api
from parkstay.admin import admin

from ledger.urls import urlpatterns as ledger_patterns

# API patterns
router = routers.DefaultRouter()
router.register(r'campground_map', api.CampgroundMapViewSet)
router.register(r'campground_map_filter', api.CampgroundMapFilterViewSet)
router.register(r'campgrounds', api.CampgroundViewSet)
router.register(r'campsites', api.CampsiteViewSet)
router.register(r'campsite_bookings', api.CampsiteBookingViewSet)
router.register(r'promo_areas',api.PromoAreaViewSet)
router.register(r'parks',api.ParkViewSet)
router.register(r'features',api.FeatureViewSet)
router.register(r'regions',api.RegionViewSet)
router.register(r'campsite_classes',api.CampsiteClassViewSet)
router.register(r'booking',api.BookingViewSet)
router.register(r'campground_booking_ranges',api.CampgroundBookingRangeViewset)
router.register(r'campsite_booking_ranges',api.CampsiteBookingRangeViewset)
router.register(r'campsite_rate',api.CampsiteRateViewSet)
router.register(r'campsites_stay_history',api.CampsiteStayHistoryViewSet)
router.register(r'rates',api.RateViewset)
router.register(r'closureReasons',api.ClosureReasonViewSet)
router.register(r'openReasons',api.OpenReasonViewSet)
router.register(r'priceReasons',api.PriceReasonViewSet)
router.register(r'maxStayReasons',api.MaximumStayReasonViewSet)

api_patterns = [
    url(r'api/bulkPricing', api.BulkPricingView.as_view(),name='bulkpricing-api'),
    url(r'api/',include(router.urls))
]

# URL Patterns
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include(api_patterns)),
    url(r'^$', views.ParkstayRoutingView.as_view(), name='ps_home'),
    url(r'^my_bookings/$', views.MyBookingsView.as_view(), name='my-bookings'),
    url(r'^campsites/(?P<ground_id>[0-9]+)/$', views.CampsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    url(r'^campsite_classes/(?P<ground_id>[0-9]+)/$', views.CampsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    url(r'^ical/campground/(?P<ground_id>[0-9]+)/$', views.CampgroundFeed(), name='campground_calendar'),
    url(r'^dashboard/campgrounds$', views.DashboardView.as_view(), name='dash-campgrounds'),
    url(r'^dashboard/campsite-types$', views.DashboardView.as_view(), name='dash-campsite-types'),
    url(r'^dashboard/bookings$', views.DashboardView.as_view(), name='dash-bookings'),
    url(r'^dashboard/bulkpricing$', views.DashboardView.as_view(), name='dash-bulkpricing'),
    url(r'^dashboard/', views.DashboardView.as_view(), name='dash'),
    url(r'^booking/', views.MyBookingsView.as_view(), name='dash'),
    url(r'^map/', views.MapView.as_view(), name='map'),
] + ledger_patterns

if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
