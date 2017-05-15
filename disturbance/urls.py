from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from disturbance import views, api
from disturbance.admin import admin

from ledger.urls import urlpatterns as ledger_patterns

# API patterns
router = routers.DefaultRouter()
#router.register(r'maxStayReasons',api.MaximumStayReasonViewSet)

api_patterns = [
    url(r'api/',include(router.urls))
]

# URL Patterns
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include(api_patterns)),
    url(r'^$', views.DisturbanceRoutingView.as_view(), name='ds_home'),
    url(r'^dashboard/$', views.DashboardView.as_view(), name='dash'),
    url(r'^external/$', views.MyProposalsView.as_view(), name='external'),
    url(r'^firsttime/$', views.first_time, name='first_time'),
    url(r'^update/$', views.UserProfileUpdate.as_view(), name='user_profile_update'),
    url(r'^addresses/create/(?P<type>\w+)/$', views.UserAddressCreate.as_view(), name='user_address_create'),
    url(r'^addresses/(?P<pk>\d+)/update/$', views.AddressUpdate.as_view(), name='address_update'),
    url(r'^addresses/(?P<pk>\d+)/delete/$', views.AddressDelete.as_view(), name='address_delete'),
    url(r'^organisations/$', views.OrganisationList.as_view(), name='organisation_list'),
    url(r'^organisations/create/$', views.OrganisationCreate.as_view(), name='organisation_create'),
    url(r'^organisations/(?P<pk>\d+)/$', views.OrganisationDetail.as_view(), name='organisation_detail'),
    url(r'^organisations/(?P<pk>\d+)/update/$', views.OrganisationUpdate.as_view(), name='organisation_update'),
    url(r'^organisations/(?P<pk>\d+)/create-address/(?P<type>\w+)/$', views.OrganisationAddressCreate.as_view(), name='organisation_address_create'),
    url(r'^organisations/(?P<pk>\d+)/request-delegate-access/$', views.RequestDelegateAccess.as_view(), name='organisation_request_delegate_access'),
    url(r'^organisations/(?P<pk>\d+)/confirm-delegate-access/(?P<uid>[0-9A-Za-z]+)-(?P<token>.+)/$', views.ConfirmDelegateAccess.as_view(), name='organisation_confirm_delegate_access'),
    url(r'^organisations/(?P<pk>\d+)/unlink-delegate/(?P<user_id>\w+)/$', views.OrganisationUnlinkDelegate.as_view(), name='organisation_unlink_delegate'),
] + ledger_patterns

if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
