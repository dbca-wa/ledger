import logging
from django.conf import settings
from django.conf.urls import url, include
from django.views.generic.base import TemplateView, RedirectView
from django.conf.urls.static import static
from rest_framework import routers

from wildlifecompliance import views
from wildlifecompliance.components.applications.views import (
    ApplicationSuccessView,
    LicenceFeeSuccessView,
)
from wildlifecompliance.admin import wildlifecompliance_admin_site

from wildlifecompliance.components.main.views import SearchKeywordsView, SearchReferenceView
from wildlifecompliance.components.applications import views as application_views
from wildlifecompliance.components.offence.api import OffenceViewSet
from wildlifecompliance.components.users import api as users_api
from wildlifecompliance.components.organisations import api as org_api
from wildlifecompliance.components.applications import api as application_api
from wildlifecompliance.components.licences import api as licence_api
from wildlifecompliance.components.returns import api as return_api
from wildlifecompliance.management.permissions_manager import CollectorManager
from wildlifecompliance.components.call_email import api as call_email_api
from wildlifecompliance.components.offence import api as offence_api

from wildlifecompliance.utils import are_migrations_running

from ledger.urls import urlpatterns as ledger_patterns

logger = logging.getLogger(__name__)

# API patterns
router = routers.DefaultRouter()
router.register(r'application', application_api.ApplicationViewSet)
router.register(r'application_paginated',
                application_api.ApplicationPaginatedViewSet)
router.register(r'application_conditions',
                application_api.ApplicationConditionViewSet)
router.register(r'application_standard_conditions',
                application_api.ApplicationStandardConditionViewSet)
router.register(r'assessment', application_api.AssessmentViewSet)
router.register(r'assessment_paginated',
                application_api.AssessmentPaginatedViewSet)
router.register(r'amendment', application_api.AmendmentRequestViewSet)
router.register(r'assessor_group', application_api.AssessorGroupViewSet)
router.register(r'licences', licence_api.LicenceViewSet)
router.register(r'licences_paginated', licence_api.LicencePaginatedViewSet)
router.register(r'licences_class', licence_api.LicenceCategoryViewSet)
router.register(r'licence_available_purposes',
                licence_api.UserAvailableWildlifeLicencePurposesViewSet)
router.register(r'returns', return_api.ReturnViewSet)
router.register(r'return_types', return_api.ReturnTypeViewSet)
router.register(r'organisations', org_api.OrganisationViewSet)
router.register(r'organisations_paginated',
                org_api.OrganisationPaginatedViewSet)
router.register(r'organisation_requests', org_api.OrganisationRequestsViewSet)
router.register(r'organisation_requests_paginated',
                org_api.OrganisationRequestsPaginatedViewSet)
router.register(r'organisation_contacts', org_api.OrganisationContactViewSet)
router.register(r'my_organisations', org_api.MyOrganisationsViewSet)
router.register(r'users', users_api.UserViewSet)
router.register(r'users_paginated', users_api.UserPaginatedViewSet)
router.register(r'profiles', users_api.ProfileViewSet)
router.register(r'my_profiles', users_api.MyProfilesViewSet)
router.register(r'emailidentities', users_api.EmailIdentityViewSet)
router.register(r'call_email', call_email_api.CallEmailViewSet)
router.register(r'call_email_location', call_email_api.LocationViewSet)
router.register(r'classification', call_email_api.ClassificationViewSet)
router.register(r'report_types', call_email_api.ReportTypeViewSet)
router.register(r'location', call_email_api.LocationViewSet)
router.register(r'referrers', call_email_api.ReferrerViewSet)
router.register(r'search_user', call_email_api.EmailUserViewSet)
router.register(r'search_alleged_offences', offence_api.SearchSectionRegulation)
router.register(r'map_layers', call_email_api.MapLayerViewSet)
router.register(r'compliancepermissiongroup', users_api.CompliancePermissionGroupViewSet)
router.register(r'region_district', users_api.RegionDistrictViewSet)
router.register(r'case_priorities', call_email_api.CasePriorityViewSet)
router.register(r'inspection_types', call_email_api.InspectionTypeViewSet)
router.register(r'offence', offence_api.OffenceViewSet)

api_patterns = [url(r'^api/my_user_details/$',
                    users_api.GetMyUserDetails.as_view(),
                    name='get-my-user-details'),
                url(r'^api/my_compliance_user_details/$',
                    users_api.GetComplianceUserDetails.as_view(),
                    name='get-my-compliance-user-details'),
                url(r'^api/is_new_user/$',
                    users_api.IsNewUser.as_view(),
                    name='is-new-user'),
                url(r'^api/user_profile_completed/$',
                    users_api.UserProfileCompleted.as_view(),
                    name='get-user-profile-completed'),
                url(r'^api/amendment_request_reason_choices',
                    application_api.AmendmentRequestReasonChoicesView.as_view(),
                    name='amendment_request_reason_choices'),
                url(r'^api/empty_list/$',
                    application_api.GetEmptyList.as_view(),
                    name='get-empty-list'),
                url(r'^api/organisation_access_group_members',
                    org_api.OrganisationAccessGroupMembers.as_view(),
                    name='organisation-access-group-members'),
                url(r'^api/search_keywords',
                    SearchKeywordsView.as_view(),
                    name='search_keywords'),
                url(r'^api/search_reference',
                    SearchReferenceView.as_view(),
                    name='search_reference'),
                url(r'^api/',
                    include(router.urls))]

# URL Patterns
urlpatterns = [
    url(r'contact-us/$',
        TemplateView.as_view(
            template_name="wildlifecompliance/contact_us.html"),
        name='wc_contact'),
    url(
        r'further-info/$',
        RedirectView.as_view(
            url='https://www.dpaw.wa.gov.au/plants-and-animals/licences-and-permits'),
        name='wc_further_info'),
    url(r'^admin/', wildlifecompliance_admin_site.urls),
    url(r'', include(api_patterns)),
    url(r'^$', views.WildlifeComplianceRoutingView.as_view(), name='wc_home'),
    url(r'^internal/', views.InternalView.as_view(), name='internal'),
    url(r'^external/', views.ExternalView.as_view(), name='external'),
    url(r'^external/application/(?P<application_pk>\d+)/$',
        views.ExternalApplicationView.as_view(),
        name='external-application-detail'),
    url(r'^external/return/(?P<return_pk>\d+)/$',
        views.ExternalReturnView.as_view(),
        name='external-return-detail'),
    url(r'^firsttime/$', views.first_time, name='first_time'),
    url(r'^account/$', views.ExternalView.as_view(), name='manage-account'),
    url(r'^profiles/', views.ExternalView.as_view(), name='manage-profiles'),
    # url(r'^external/organisations/manage/$', views.ExternalView.as_view(), name='manage-org'),
    url(r'^application/$',
        application_views.ApplicationView.as_view(),
        name='application'),
    # url(r'^organisations/(?P<pk>\d+)/confirm-delegate-access/(?P<uid>[0-9A-Za-z]+)-(?P<token>.+)/$',
    #     views.ConfirmDelegateAccess.as_view(), name='organisation_confirm_delegate_access'),
    url('^healthcheck/', views.HealthCheckView.as_view(), name='health_check'),

    # following url is defined so that to include url path when sending
    # application emails to users
    url(r'^internal/application/(?P<application_pk>\d+)/$', views.ApplicationView.as_view(),
        name='internal-application-detail'),
    url(r'^application_submit/submit_with_invoice/',
        ApplicationSuccessView.as_view(),
        name='external-application-success-invoice'),
    url(r'^application/finish_licence_fee_payment/',
        LicenceFeeSuccessView.as_view(),
        name='external-licence-fee-success-invoice'),

    # following url is defined so that to include url path when sending
    # call_email emails to users
    url(r'^internal/call_email/(?P<call_email_id>\d+)/$', views.ApplicationView.as_view(),
        name='internal-call-email-detail'),
    
    # url(r'^export/xls/$', application_views.export_applications, name='export_applications'),
    url(r'^export/pdf/$', application_views.pdflatex, name='pdf_latex'),
    url(r'^mgt-commands/$',
        views.ManagementCommandsView.as_view(),
        name='mgt-commands'),

] + ledger_patterns

if not are_migrations_running():
    CollectorManager()

if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
