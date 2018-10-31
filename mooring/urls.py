from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from mooring import views, api
from mooring.admin import admin

from ledger.urls import urlpatterns as ledger_patterns

# API patterns
router = routers.DefaultRouter()
router.register(r'mooring_map', api.MooringAreaMapViewSet)
router.register(r'mooring_map_filter', api.MooringAreaMapFilterViewSet)
router.register(r'marine_parks_map', api.MarineParksMapViewSet)
router.register(r'region_marine_parks_map', api.MarineParksRegionMapViewSet)
router.register(r'availability', api.AvailabilityViewSet, 'availability')
router.register(r'availability_admin', api.AvailabilityAdminViewSet)
router.register(r'availability_ratis', api.AvailabilityRatisViewSet, 'availability_ratis')
router.register(r'mooring-areas', api.MooringAreaViewSet)
router.register(r'mooringsites', api.MooringsiteViewSet)
router.register(r'mooringsite_bookings', api.MooringsiteBookingViewSet)
router.register(r'promo_areas', api.PromoAreaViewSet)
router.register(r'parks', api.MarinaViewSet)
router.register(r'parkentryrate', api.MarinaEntryRateViewSet)
router.register(r'features', api.FeatureViewSet)
router.register(r'regions', api.RegionViewSet)
router.register(r'mooring_groups', api.MooringGroup)
router.register(r'districts', api.DistrictViewSet)
router.register(r'mooringsite_classes', api.MooringsiteClassViewSet)
router.register(r'booking',api.BookingViewSet)
router.register(r'mooring_booking_ranges',api.MooringAreaBookingRangeViewset)
router.register(r'mooringsite_booking_ranges',api.MooringsiteBookingRangeViewset)
router.register(r'mooringsite_rate',api.MooringsiteRateViewSet)
router.register(r'mooringsites_stay_history',api.MooringsiteStayHistoryViewSet)
router.register(r'mooring_stay_history',api.MooringAreaStayHistoryViewSet)
router.register(r'rates',api.RateViewset)
router.register(r'closureReasons',api.ClosureReasonViewSet)
router.register(r'openReasons',api.OpenReasonViewSet)
router.register(r'priceReasons',api.PriceReasonViewSet)
router.register(r'maxStayReasons',api.MaximumStayReasonViewSet)
router.register(r'users',api.UsersViewSet)
router.register(r'contacts',api.ContactViewSet)
router.register(r'countries', api.CountryViewSet)

api_patterns = [
    url(r'^api/profile$',api.GetProfile.as_view(), name='get-profile'),
    url(r'^api/profile/update_personal$',api.UpdateProfilePersonal.as_view(), name='update-profile-personal'),
    url(r'^api/profile/update_contact$',api.UpdateProfileContact.as_view(), name='update-profile-contact'),
    url(r'^api/profile/update_address$',api.UpdateProfileAddress.as_view(), name='update-profile-address'),
    url(r'^api/oracle_job$',api.OracleJob.as_view(), name='get-oracle'),
    url(r'^api/bulkPricing', api.BulkPricingView.as_view(),name='bulkpricing-api'),
    url(r'^api/search_suggest', api.search_suggest, name='search_suggest'),
    url(r'^api/create_booking', api.create_booking, name='create_booking'),
    url(r'api/get_confirmation/(?P<booking_id>[0-9]+)/$', api.get_confirmation, name='get_confirmation'),
    url(r'^api/reports/booking_refunds$', api.BookingRefundsReportView.as_view(),name='booking-refunds-report'),
    url(r'^api/reports/bookings$', api.BookingReportView.as_view(),name='bookings-report'),
    url(r'^api/reports/booking_settlements$', api.BookingSettlementReportView.as_view(),name='booking-settlements-report'),
    url(r'^api/',include(router.urls))
]

# URL Patterns
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include(api_patterns)),
    url(r'^account/', views.ProfileView.as_view(), name='account'),
    url(r'^$', views.MarinastayRoutingView.as_view(), name='ps_home'),
    url(r'^mooringsites/(?P<ground_id>[0-9]+)/$', views.MooringsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    url(r'^availability/$', views.MooringsiteAvailabilitySelector.as_view(), name='campsite_availaiblity_selector'),
    url(r'^availability_admin/$', views.AvailabilityAdmin.as_view(), name='availability_admin'),
    #url(r'^ical/campground/(?P<ground_id>[0-9]+)/$', views.MooringAreaFeed(), name='campground_calendar'),
    url(r'^dashboard/moorings/$', views.DashboardView.as_view(), name='dash-campgrounds'),
    url(r'^dashboard/mooringsite-types$', views.DashboardView.as_view(), name='dash-campsite-types'),
    url(r'^dashboard/bookings/edit/', views.DashboardView.as_view(), name='dash-bookings'),
    url(r'^dashboard/bookings$', views.DashboardView.as_view(), name='dash-bookings'),
    url(r'^dashboard/bulkpricing$', views.DashboardView.as_view(), name='dash-bulkpricing'),
    url(r'^dashboard/', views.DashboardView.as_view(), name='dash'),
    url(r'^booking/abort$', views.abort_booking_view, name='public_abort_booking'),
    url(r'^booking/', views.MakeBookingsView.as_view(), name='public_make_booking'),
    url(r'^mybookings/', views.MyBookingsView.as_view(), name='public_my_bookings'),
    url(r'^success/', views.BookingSuccessView.as_view(), name='public_booking_success'),
    url(r'^map/', views.MapView.as_view(), name='map'),
    url(r'mooring/payments/invoice-pdf/(?P<reference>\d+)',views.InvoicePDFView.as_view(), name='mooring-invoice-pdf'),
##    url(r'^static/(?P<path>.*)$', 'django.conf.urls.static'),
#    {'document_root': settings.STATIC_ROOT},
] + ledger_patterns 


if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
