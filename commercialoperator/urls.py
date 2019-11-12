from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from commercialoperator import views
from commercialoperator.admin import commercialoperator_admin_site
from commercialoperator.components.proposals import views as proposal_views
from commercialoperator.components.organisations import views as organisation_views
from commercialoperator.components.bookings import views as booking_views

from commercialoperator.components.users import api as users_api
from commercialoperator.components.organisations import api as org_api
from commercialoperator.components.proposals import api as proposal_api
from commercialoperator.components.approvals import api as approval_api
from commercialoperator.components.compliances import api as compliances_api
from commercialoperator.components.main import api as main_api
from commercialoperator.components.bookings import api as booking_api

from ledger.urls import urlpatterns as ledger_patterns

# API patterns
router = routers.DefaultRouter()
router.register(r'organisations',org_api.OrganisationViewSet)
router.register(r'proposal',proposal_api.ProposalViewSet)
router.register(r'proposal_park',proposal_api.ProposalParkViewSet)
router.register(r'proposal_submit',proposal_api.ProposalSubmitViewSet)
router.register(r'proposal_paginated',proposal_api.ProposalPaginatedViewSet)
router.register(r'approval_paginated',approval_api.ApprovalPaginatedViewSet)
router.register(r'booking_paginated',booking_api.BookingPaginatedViewSet)
#router.register(r'parkbooking_paginated',booking_api.ParkBookingPaginatedViewSet)
router.register(r'compliance_paginated',compliances_api.CompliancePaginatedViewSet)
router.register(r'referrals',proposal_api.ReferralViewSet)
router.register(r'approvals',approval_api.ApprovalViewSet)
router.register(r'bookings',booking_api.BookingViewSet)
router.register(r'park_bookings',booking_api.ParkBookingViewSet)
router.register(r'compliances',compliances_api.ComplianceViewSet)
router.register(r'proposal_requirements',proposal_api.ProposalRequirementViewSet)
router.register(r'proposal_standard_requirements',proposal_api.ProposalStandardRequirementViewSet)
router.register(r'organisation_requests',org_api.OrganisationRequestsViewSet)
router.register(r'organisation_contacts',org_api.OrganisationContactViewSet)
router.register(r'my_organisations',org_api.MyOrganisationsViewSet)
router.register(r'users',users_api.UserViewSet)
#router.register(r'users2',users_api.UserListView)
#router.register(r'profiles', users_api.ProfileViewSet)
router.register(r'amendment_request',proposal_api.AmendmentRequestViewSet)
router.register(r'compliance_amendment_request',compliances_api.ComplianceAmendmentRequestViewSet)
router.register(r'regions', main_api.RegionViewSet)
router.register(r'global_settings', main_api.GlobalSettingsViewSet)
router.register(r'activity_matrix', main_api.ActivityMatrixViewSet)
#router.register(r'tenure', main_api.TenureViewSet)
router.register(r'application_types', main_api.ApplicationTypeViewSet)
router.register(r'access_types', main_api.AccessTypeViewSet)
router.register(r'vessels', proposal_api.VesselViewSet)
#router.register(r'assessor_checklist', proposal_api.AssessorChecklistViewSet)
router.register(r'assessments', proposal_api.ProposalAssessmentViewSet)
router.register(r'parks', main_api.ParkViewSet)
#router.register(r'park_treeview', main_api.RegionViewSet2)
router.register(r'tclass_container_land', main_api.LandActivityTabViewSet, base_name='tclass_container_land')
router.register(r'tclass_container_marine', main_api.MarineActivityTabViewSet, base_name='tclass_container_marine')
router.register(r'trails', main_api.TrailViewSet)
router.register(r'vehicles', proposal_api.VehicleViewSet)
router.register(r'land_activities', main_api.LandActivitiesViewSet)
router.register(r'marine_activities', main_api.MarineActivitiesViewSet)
router.register(r'required_documents', main_api.RequiredDocumentViewSet)
router.register(r'questions', main_api.QuestionViewSet)
router.register(r'payment', main_api.PaymentViewSet)

api_patterns = [
    url(r'^api/profile$', users_api.GetProfile.as_view(), name='get-profile'),
    url(r'^api/department_users$', users_api.DepartmentUserList.as_view(), name='department-users-list'),
    url(r'^api/filtered_users$', users_api.UserListFilterView.as_view(), name='filtered_users'),
    url(r'^api/filtered_organisations$', org_api.OrganisationListFilterView.as_view(), name='filtered_organisations'),
    url(r'^api/filtered_payments$', approval_api.ApprovalPaymentFilterViewSet.as_view(), name='filtered_payments'),
    url(r'^api/proposal_type$', proposal_api.GetProposalType.as_view(), name='get-proposal-type'),
    url(r'^api/empty_list$', proposal_api.GetEmptyList.as_view(), name='get-empty-list'),
    url(r'^api/organisation_access_group_members',org_api.OrganisationAccessGroupMembers.as_view(),name='organisation-access-group-members'),
    url(r'^api/',include(router.urls)),
    url(r'^api/amendment_request_reason_choices',proposal_api.AmendmentRequestReasonChoicesView.as_view(),name='amendment_request_reason_choices'),
    url(r'^api/compliance_amendment_reason_choices',compliances_api.ComplianceAmendmentReasonChoicesView.as_view(),name='amendment_request_reason_choices'),
    url(r'^api/search_keywords',proposal_api.SearchKeywordsView.as_view(),name='search_keywords'),
    url(r'^api/search_reference',proposal_api.SearchReferenceView.as_view(),name='search_reference'),
    url(r'^api/accreditation_choices',proposal_api.AccreditationTypeView.as_view(),name='accreditation_choices'),
    url(r'^api/licence_period_choices',proposal_api.LicencePeriodChoicesView.as_view(),name='licence_period_choices'),

    url(r'^api/oracle_job$',main_api.OracleJob.as_view(), name='get-oracle'),
    #url(r'^api/reports/bookings$', api.BookingReportView.as_view(),name='bookings-report'),


    url(r'^api/reports/booking_settlements$', main_api.BookingSettlementReportView.as_view(),name='booking-settlements-report'),
]

# URL Patterns
urlpatterns = [
    #url(r'^admin/', include(commercialoperator_admin_site.urls)),
    url(r'^admin/', commercialoperator_admin_site.urls),
    url(r'', include(api_patterns)),
    url(r'^$', views.CommercialOperatorRoutingView.as_view(), name='ds_home'),
    url(r'^contact/', views.CommercialOperatorContactView.as_view(), name='ds_contact'),
    url(r'^further_info/', views.CommercialOperatorFurtherInformationView.as_view(), name='ds_further_info'),
    url(r'^internal/', views.InternalView.as_view(), name='internal'),
    url(r'^internal/proposal/(?P<proposal_pk>\d+)/referral/(?P<referral_pk>\d+)/$', views.ReferralView.as_view(), name='internal-referral-detail'),
    url(r'^external/', views.ExternalView.as_view(), name='external'),
    url(r'^firsttime/$', views.first_time, name='first_time'),
    url(r'^account/$', views.ExternalView.as_view(), name='manage-account'),
    url(r'^profiles/', views.ExternalView.as_view(), name='manage-profiles'),
    url(r'^help/(?P<application_type>[^/]+)/(?P<help_type>[^/]+)/$', views.HelpView.as_view(), name='help'),
    url(r'^mgt-commands/$', views.ManagementCommandsView.as_view(), name='mgt-commands'),
    url(r'test-emails/$', proposal_views.TestEmailView.as_view(), name='test-emails'),
    #url(r'^external/organisations/manage/$', views.ExternalView.as_view(), name='manage-org'),
    #following url is used to include url path when sending Proposal amendment request to user.
    url(r'^proposal/$', proposal_views.ProposalView.as_view(), name='proposal'),
    url(r'^preview/licence-pdf/(?P<proposal_pk>\d+)',proposal_views.PreviewLicencePDFView.as_view(), name='preview_licence_pdf'),

    # payment related urls
    url(r'^application_fee/(?P<proposal_pk>\d+)/$', booking_views.ApplicationFeeView.as_view(), name='application_fee'),
    url(r'^payment/(?P<proposal_pk>\d+)/$', booking_views.MakePaymentView.as_view(), name='make_payment'),
    url(r'^payment_deferred/(?P<proposal_pk>\d+)/$', booking_views.DeferredInvoicingView.as_view(), name='deferred_invoicing'),
    url(r'^preview_deferred/(?P<proposal_pk>\d+)/$', booking_views.DeferredInvoicingPreviewView.as_view(), name='preview_deferred_invoicing'),
    url(r'^success/booking/$', booking_views.BookingSuccessView.as_view(), name='public_booking_success'),
    url(r'^success/fee/$', booking_views.ApplicationFeeSuccessView.as_view(), name='fee_success'),
    url(r'cols/payments/invoice-pdf/(?P<reference>\d+)',booking_views.InvoicePDFView.as_view(), name='cols-invoice-pdf'),
    url(r'cols/payments/confirmation-pdf/(?P<reference>\d+)',booking_views.ConfirmationPDFView.as_view(), name='cols-confirmation-pdf'),
    url(r'cols/payments/monthly-confirmation-pdf/(?P<id>\d+)',booking_views.MonthlyConfirmationPDFView.as_view(), name='cols-monthly-confirmation-pdf'),

    #following url is defined so that to include url path when sending Proposal amendment request to user.
    url(r'^external/proposal/(?P<proposal_pk>\d+)/$', views.ExternalProposalView.as_view(), name='external-proposal-detail'),
    url(r'^internal/proposal/(?P<proposal_pk>\d+)/$', views.InternalProposalView.as_view(), name='internal-proposal-detail'),
    url(r'^external/compliance/(?P<compliance_pk>\d+)/$', views.ExternalComplianceView.as_view(), name='external-compliance-detail'),
    url(r'^internal/compliance/(?P<compliance_pk>\d+)/$', views.InternalComplianceView.as_view(), name='internal-compliance-detail'),

    #url(r'^organisations/(?P<pk>\d+)/confirm-delegate-access/(?P<uid>[0-9A-Za-z]+)-(?P<token>.+)/$', views.ConfirmDelegateAccess.as_view(), name='organisation_confirm_delegate_access'),
    # reversion history-compare
    url(r'^history/proposal/(?P<pk>\d+)/$', proposal_views.ProposalHistoryCompareView.as_view(), name='proposal_history'),
    url(r'^history/filtered/(?P<pk>\d+)/$', proposal_views.ProposalFilteredHistoryCompareView.as_view(), name='proposal_filtered_history'),
    url(r'^history/referral/(?P<pk>\d+)/$', proposal_views.ReferralHistoryCompareView.as_view(), name='referral_history'),
    url(r'^history/approval/(?P<pk>\d+)/$', proposal_views.ApprovalHistoryCompareView.as_view(), name='approval_history'),
    url(r'^history/compliance/(?P<pk>\d+)/$', proposal_views.ComplianceHistoryCompareView.as_view(), name='compliance_history'),
    url(r'^history/proposaltype/(?P<pk>\d+)/$', proposal_views.ProposalTypeHistoryCompareView.as_view(), name='proposaltype_history'),
    url(r'^history/helppage/(?P<pk>\d+)/$', proposal_views.HelpPageHistoryCompareView.as_view(), name='helppage_history'),
    url(r'^history/organisation/(?P<pk>\d+)/$', organisation_views.OrganisationHistoryCompareView.as_view(), name='organisation_history'),


] + ledger_patterns

if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
