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
#router.register(r'current_booking', api.CurrentBookingViewSet)
router.register(r'mooring_map_filter', api.MooringAreaMapFilterViewSet)
router.register(r'marine_parks_map', api.MarineParksMapViewSet)
router.register(r'region_marine_parks_map', api.MarineParksRegionMapViewSet)
#router.register(r'availability', api.AvailabilityViewSet, 'availability')
router.register(r'availability2', api.AvailabilityViewSet2, 'availability2')
router.register(r'availability_admin', api.AvailabilityAdminViewSet)
router.register(r'availability_ratis', api.AvailabilityRatisViewSet, 'availability_ratis')
router.register(r'mooring-areas', api.MooringAreaViewSet)
router.register(r'mooringsites', api.MooringsiteViewSet)
router.register(r'mooringsite_bookings', api.MooringsiteBookingViewSet)
router.register(r'promo_areas', api.PromoAreaViewSet)
router.register(r'parks', api.MarinaViewSet)
router.register(r'admissions', api.AdmissionsRatesViewSet)
router.register(r'parkentryrate', api.MarinaEntryRateViewSet)
router.register(r'features', api.FeatureViewSet)
router.register(r'regions', api.RegionViewSet)
router.register(r'mooring_groups', api.MooringGroup)
router.register(r'districts', api.DistrictViewSet)
router.register(r'mooringsite_classes', api.MooringsiteClassViewSet)
router.register(r'booking',api.BookingViewSet)
router.register(r'admissionsbooking',api.AdmissionsBookingViewSet)
router.register(r'mooring_booking_ranges',api.MooringAreaBookingRangeViewset)
router.register(r'mooringsite_booking_ranges',api.MooringsiteBookingRangeViewset)
# router.register(r'mooringsite_rate',api.MooringsiteRateViewSet)
router.register(r'mooringsites_stay_history',api.MooringsiteStayHistoryViewSet)
router.register(r'mooring_stay_history',api.MooringAreaStayHistoryViewSet)
router.register(r'rates',api.RateViewset)
router.register(r'closureReasons',api.ClosureReasonViewSet)
router.register(r'openReasons',api.OpenReasonViewSet)
router.register(r'priceReasons',api.PriceReasonViewSet)
router.register(r'admissionsReasons',api.AdmissionsReasonViewSet)
router.register(r'maxStayReasons',api.MaximumStayReasonViewSet)
router.register(r'discountReasons', api.DiscountReasonViewSet)
router.register(r'users',api.UsersViewSet)
router.register(r'contacts',api.ContactViewSet)
router.register(r'countries', api.CountryViewSet)
router.register(r'bookingPeriodOptions', api.BookingPeriodOptionsViewSet)
router.register(r'bookingPeriod', api.BookingPeriodViewSet)
router.register(r'registeredVessels', api.RegisteredVesselsViewSet)

api_patterns = [
    url(r'^api/profile$',api.GetProfile.as_view(), name='get-profile'),
    url(r'^api/profile-admin$',api.GetProfileAdmin.as_view(), name='get-profile-admin'),
    url(r'^api/profile/update_personal$',api.UpdateProfilePersonal.as_view(), name='update-profile-personal'),
    url(r'^api/profile/update_contact$',api.UpdateProfileContact.as_view(), name='update-profile-contact'),
    url(r'^api/profile/update_address$',api.UpdateProfileAddress.as_view(), name='update-profile-address'),
    url(r'^api/oracle_job$',api.OracleJob.as_view(), name='get-oracle'),
    url(r'^api/bulkPricing', api.BulkPricingView.as_view(),name='bulkpricing-api'),
    url(r'^api/search_suggest', api.search_suggest, name='search_suggest'),
    url(r'^api/create_booking', api.create_booking, name='create_booking'),
    url(r'^api/create_admissions_booking', api.create_admissions_booking, name="create_admissions_booking"),
    url(r'api/get_confirmation/(?P<booking_id>[0-9]+)/$', api.get_confirmation, name='get_confirmation'),
    url(r'api/get_admissions_confirmation/(?P<booking_id>[0-9]+)/$', api.get_admissions_confirmation, name='get_admissions_confirmation'),
    url(r'^api/reports/booking_refunds$', api.BookingRefundsReportView.as_view(),name='booking-refunds-report'),
    url(r'^api/reports/bookings$', api.BookingReportView.as_view(),name='bookings-report'),
    url(r'^api/reports/booking_settlements$', api.BookingSettlementReportView.as_view(),name='booking-settlements-report'),
    url(r'^api/booking/create$', api.add_booking,name='add_booking'),
    url(r'^api/booking/delete$', api.delete_booking,name='del_booking'),
    url(r'^api/current_booking$', api.current_booking,name='current_booking'),
    url(r'^api/global_settings$', api.GlobalSettingsView.as_view(), name='global_setting'),
    url(r'^api/check_oracle_code$', api.CheckOracleCodeView.as_view(), name='check_oracle_code'),
    url(r'^api/refund_oracle$', api.RefundOracleView.as_view(), name='refund_oracle'),
#    url(r'^api/admissions_key$', api.AdmissionsKeyFromURLView.as_view(), name='admissions_key'),
    url(r'^api/',include(router.urls))
]

# URL Patterns
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include(api_patterns)),
    url(r'^forbidden', views.ForbiddenView.as_view(), name='forbidden-view'),
    url(r'^account/', views.ProfileView.as_view(), name='account'),
    url(r'^$', views.MarinastayRoutingView.as_view(), name='ps_home'),
    url(r'^mooringsites/(?P<ground_id>[0-9]+)/$', views.MooringsiteBookingSelector.as_view(), name='campsite_booking_selector'),
    url(r'^availability/$', views.MooringsiteAvailabilitySelector.as_view(), name='campsite_availaiblity_selector'),
    url(r'^availability2/$', views.MooringAvailability2Selector.as_view(), name='mooring_availaiblity2_selector'),
    url(r'^availability_admin/$', views.AvailabilityAdmin.as_view(), name='availability_admin'),
    #url(r'^ical/campground/(?P<ground_id>[0-9]+)/$', views.MooringAreaFeed(), name='campground_calendar'),
    url(r'^dashboard/moorings/$', views.DashboardView.as_view(), name='dash-campgrounds'),
    url(r'^dashboard/mooringsite-types$', views.DashboardView.as_view(), name='dash-campsite-types'),
    url(r'^dashboard/bookings/edit/', views.DashboardView.as_view(), name='dash-bookings'),
    url(r'^dashboard/bookings$', views.DashboardView.as_view(), name='dash-bookings'),
    url(r'^dashboard/bulkpricing$', views.DashboardView.as_view(), name='dash-bulkpricing'),
    url(r'^dashboard/booking-policy-change/(?P<pk>[0-9]+)/edit', views.BookingPolicyEditChangeGroup.as_view(), name='dash-booking-policy-change-edit'),
    url(r'^dashboard/booking-policy-change/(?P<pk>[0-9]+)', views.BookingPolicyChangeView.as_view(), name='dash-booking-policy-change-view'),
    url(r'^dashboard/booking-policy-cancel/(?P<pk>[0-9]+)/edit', views.BookingPolicyEditCancelGroup.as_view(), name='dash-booking-policy-cancel-edit'),
    url(r'^dashboard/booking-policy-cancel/(?P<pk>[0-9]+)', views.BookingPolicyCancelView.as_view(), name='dash-booking-policy-cancel-view'),
    url(r'^dashboard/booking-policy-change-option/(?P<cg>[0-9]+)/edit/(?P<pk>[0-9]+)', views.BookingPolicyEditChangeOption.as_view(), name='dash-booking-policy-change-option-edit'),
    url(r'^dashboard/booking-policy-cancel-option/(?P<cg>[0-9]+)/edit/(?P<pk>[0-9]+)', views.BookingPolicyEditCancelOption.as_view(), name='dash-booking-policy-cancel-option-edit'),
    url(r'^dashboard/booking-policy-change-option/(?P<pk>[0-9]+)', views.BookingPolicyAddChangeOption.as_view(), name='dash-booking-policy-change-option-view'),
    url(r'^dashboard/booking-policy-cancel-option/(?P<pk>[0-9]+)', views.BookingPolicyAddCancelOption.as_view(), name='dash-booking-policy-cancel-option-view'),
    url(r'^dashboard/booking-policy/create-change', views.BookingPolicyAddChangeGroup.as_view(), name='dash-booking-policy-create-change'),
    url(r'^dashboard/booking-policy/create-cancel', views.BookingPolicyAddCancelGroup.as_view(), name='dash-booking-policy-create-cancel'),
    url(r'^dashboard/booking-policy', views.BookingPolicyView.as_view(), name='dash-bookingpolicy'),
    url(r'^dashboard/booking-periods-option/(?P<bp_group_id>[0-9]+)/create', views.BookingPeriodAddOption.as_view(), name='dash-booking-period-option-add'),
    url(r'^dashboard/booking-periods-option/(?P<bp_group_id>[0-9]+)/edit/(?P<pk>[0-9]+)', views.BookingPeriodEditOption.as_view(), name='dash-booking-period-option-edit'),
    url(r'^dashboard/booking-periods-option/(?P<bp_group_id>[0-9]+)/delete/(?P<pk>[0-9]+)', views.BookingPeriodDeleteOption.as_view(), name='dash-booking-period-option-delete'),
    url(r'^dashboard/bookingperiods/create', views.BookingPeriodAddChangeGroup.as_view(), name='dash-bookingperiod-group-add'),
    url(r'^dashboard/bookingperiods/(?P<pk>[0-9]+)/edit', views.BookingPeriodEditChangeGroup.as_view(), name='dash-bookingperiod-group-edit'),
    url(r'^dashboard/bookingperiods/(?P<pk>[0-9]+)/delete', views.BookingPeriodDeleteGroup.as_view(), name='dash-bookingperiod-group-delete'),
    url(r'^dashboard/bookingperiods/(?P<pk>[0-9]+)/view', views.BookingPeriodView.as_view(), name='dash-bookingperiod-group-view'),
    url(r'^dashboard/bookingperiods', views.BookingPeriodGroupView.as_view(), name='dash-bookingperiod'),
    url(r'^dashboard/failed-refunds/(?P<pk>[0-9]+)/complete', views.RefundFailedCompleted.as_view(), name='dash-complete_failed_refund'),
    url(r'^dashboard/failed-refunds-completed', views.RefundFailedCompletedView.as_view(), name='dash-failed_refunds_completed'),
    url(r'^dashboard/failed-refunds', views.RefundFailedView.as_view(), name='dash-failedrefunds'),
    url(r'^dashboard/', views.DashboardView.as_view(), name='dash'),
    #url(r'^dashboard/bookingperiods2', views.DashboardView.as_view(), name='dash-bookingperiod2'),
    url(r'^booking/abort$', views.abort_booking_view, name='public_abort_booking'),
    url(r'^booking/', views.MakeBookingsView.as_view(), name='public_make_booking'),
    url(r'^refund-payment/', views.RefundPaymentView.as_view(), name='refund_payment'),
    url(r'^no-payment/', views.ZeroBookingView.as_view(), name='no_payment_booking'),
    url(r'^mybookings/', views.MyBookingsView.as_view(), name='public_my_bookings'),
    url(r'^booking-history/(?P<pk>[0-9]+)/', views.ViewBookingHistory.as_view(), name='view_booking_history'),
    url(r'^booking-history-refund/(?P<pk>[0-9]+)/', views.RefundBookingHistory.as_view(), name='view_refund_booking_history'),
    url(r'^view-booking/(?P<pk>[0-9]+)/', views.ViewBookingView.as_view(), name='public_view_booking'),
    url(r'^change-booking/(?P<pk>[0-9]+)/', views.ChangeBookingView.as_view(), name='public_change_booking'),
    url(r'^cancel-booking/(?P<pk>[0-9]+)/', views.CancelBookingView.as_view(), name='public_cancel_booking'),
    url(r'^cancel-admissions-booking/(?P<pk>[0-9]+)/', views.CancelAdmissionsBookingView.as_view(), name='public_cancel_admissions_booking'),
    url(r'^success/', views.BookingSuccessView.as_view(), name='public_booking_success'),
    url(r'^cancel-completed/(?P<booking_id>[0-9]+)/', views.BookingCancelCompletedView.as_view(), name='public_booking_cancelled'),
    url(r'^cancel-admission-completed/(?P<booking_id>[0-9]+)/', views.AdmissionBookingCancelCompletedView.as_view(), name='public_admission_booking_cancelled'),
    url(r'^success_admissions/', views.AdmissionsBookingSuccessView.as_view(), name='public_admissions_success'),
    url(r'^createdbasket/', views.AdmissionsBasketCreated.as_view(), name='created_basket'),
    url(r'^map/', views.MapView.as_view(), name='map'),
    url(r'^admissions/(?P<loc>[a-z]+)/$', views.AdmissionFeesView.as_view(), name='admissions'),
    url(r'^admissions-cost/$', views.AdmissionsCostView.as_view(), name='admissions_cost'),
    url(r'mooring/payments/invoice-pdf/(?P<reference>\d+)',views.InvoicePDFView.as_view(), name='mooring-invoice-pdf'),
    url(r'^mooringsiteratelog/(?P<pk>[0-9]+)/', views.MooringsiteRateLogView.as_view(), name='mooringsiteratelog'),

##    url(r'^static/(?P<path>.*)$', 'django.conf.urls.static'),
#    {'document_root': settings.STATIC_ROOT},
] + ledger_patterns 


if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
