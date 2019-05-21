from django.conf import settings
from django.urls import path, re_path, include
from django.conf.urls.static import static
from rest_framework import routers
from parkstay import views, api
from parkstay.admin import admin

from ledger.urls import urlpatterns as ledger_patterns

# API patterns
router = routers.DefaultRouter()
router.register(r'campground_map', api.CampgroundMapViewSet)
router.register(r'campground_map_filter', api.CampgroundMapFilterViewSet)
router.register(r'availability', api.AvailabilityViewSet, 'availability')
router.register(r'availability_admin', api.AvailabilityAdminViewSet)
router.register(r'availability_ratis', api.AvailabilityRatisViewSet, 'availability_ratis')
router.register(r'campgrounds', api.CampgroundViewSet)
router.register(r'campsites', api.CampsiteViewSet)
router.register(r'campsite_bookings', api.CampsiteBookingViewSet)
router.register(r'promo_areas',api.PromoAreaViewSet)
router.register(r'parks',api.ParkViewSet)
router.register(r'parkentryrate',api.ParkEntryRateViewSet)
router.register(r'features',api.FeatureViewSet)
router.register(r'regions',api.RegionViewSet)
router.register(r'districts',api.DistrictViewSet)
router.register(r'campsite_classes',api.CampsiteClassViewSet)
router.register(r'booking',api.BookingViewSet)
router.register(r'campground_booking_ranges',api.CampgroundBookingRangeViewset)
router.register(r'campsite_booking_ranges',api.CampsiteBookingRangeViewset)
router.register(r'campsite_rate',api.CampsiteRateViewSet)
router.register(r'campsites_stay_history',api.CampsiteStayHistoryViewSet)
router.register(r'campground_stay_history',api.CampgroundStayHistoryViewSet)
router.register(r'rates',api.RateViewset)
router.register(r'closureReasons',api.ClosureReasonViewSet)
router.register(r'priceReasons',api.PriceReasonViewSet)
router.register(r'maxStayReasons',api.MaximumStayReasonViewSet)
router.register(r'users',api.UsersViewSet)
router.register(r'contacts',api.ContactViewSet)
router.register(r'countries', api.CountryViewSet)
router.register(r'discountReasons',api.DiscountReasonViewset)

api_patterns = [
    path('api/profile',api.GetProfile.as_view(), name='get-profile'),
    path('api/profile/update_personal',api.UpdateProfilePersonal.as_view(), name='update-profile-personal'),
    path('api/profile/update_contact',api.UpdateProfileContact.as_view(), name='update-profile-contact'),
    path('api/profile/update_address',api.UpdateProfileAddress.as_view(), name='update-profile-address'),
    path('api/oracle_job',api.OracleJob.as_view(), name='get-oracle'),
    path('api/bulkPricing', api.BulkPricingView.as_view(),name='bulkpricing-api'),
    path('api/search_suggest', api.search_suggest, name='search_suggest'),
    path('api/create_booking', api.create_booking, name='create_booking'),
    re_path(r'api/get_confirmation/(?P<booking_id>[0-9]+)/$', api.get_confirmation, name='get_confirmation'),
    path('api/reports/booking_refunds', api.BookingRefundsReportView.as_view(),name='booking-refunds-report'),
    path('api/reports/bookings', api.BookingReportView.as_view(),name='bookings-report'),
    path('api/reports/booking_settlements', api.BookingSettlementReportView.as_view(),name='booking-settlements-report'),
    path('api/',include(router.urls))
]

# URL Patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(api_patterns)),
    path('account/', views.ProfileView.as_view(), name='account'),
    path('', views.ParkstayRoutingView.as_view(), name='ps_home'),
    re_path(r'^campsites/(?P<ground_id>[0-9]+)/$', views.CampsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    path('availability/', views.CampsiteAvailabilitySelector.as_view(), name='campsite_availaiblity_selector'),
    path('availability_admin/', views.AvailabilityAdmin.as_view(), name='availability_admin'),
    path('dashboard/campgrounds', views.DashboardView.as_view(), name='dash-campgrounds'),
    path('dashboard/campsite-types', views.DashboardView.as_view(), name='dash-campsite-types'),
    path('dashboard/bookings/edit/', views.DashboardView.as_view(), name='dash-bookings'),
    path('dashboard/bookings', views.DashboardView.as_view(), name='dash-bookings'),
    path('dashboard/bulkpricing', views.DashboardView.as_view(), name='dash-bulkpricing'),
    path('dashboard/', views.DashboardView.as_view(), name='dash'),
    path('booking/abort', views.abort_booking_view, name='public_abort_booking'),
    path('booking/', views.MakeBookingsView.as_view(), name='public_make_booking'),
    path('mybookings/', views.MyBookingsView.as_view(), name='public_my_bookings'),
    path('success/', views.BookingSuccessView.as_view(), name='public_booking_success'),
    path('map/', views.MapView.as_view(), name='map'),
] + ledger_patterns

if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
