from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework import routers
from disturbance import views
from disturbance.admin import disturbance_admin_site
from disturbance.components.proposals import views as proposal_views

from disturbance.components.users import api as users_api
from disturbance.components.organisations import api as org_api
from disturbance.components.proposals import api as proposal_api

from ledger.urls import urlpatterns as ledger_patterns

# API patterns
router = routers.DefaultRouter()
router.register(r'organisations',org_api.OrganisationViewSet)
router.register(r'organisation_requests',org_api.OrganisationRequestsViewSet)
router.register(r'users',users_api.UserViewSet)

api_patterns = [
    url(r'^api/profile$', users_api.GetProfile.as_view(), name='get-profile'),
    url(r'^api/proposal_type$', proposal_api.GetProposalType.as_view(), name='get-proposal-type'),
    url(r'^api/',include(router.urls))
]

# URL Patterns
urlpatterns = [
    url(r'^admin/', disturbance_admin_site.urls),
    url(r'', include(api_patterns)),
    url(r'^$', views.DisturbanceRoutingView.as_view(), name='ds_home'),
    url(r'^internal/', views.InternalView.as_view(), name='internal'),
    url(r'^external/', views.ExternalView.as_view(), name='external'),
    url(r'^firsttime/$', views.first_time, name='first_time'),
    url(r'^account/$', views.ExternalView.as_view(), name='manage-account'),
    url(r'^proposal/$', proposal_views.ProposalView.as_view(), name='proposal'),
    #url(r'^organisations/(?P<pk>\d+)/confirm-delegate-access/(?P<uid>[0-9A-Za-z]+)-(?P<token>.+)/$', views.ConfirmDelegateAccess.as_view(), name='organisation_confirm_delegate_access'),
] + ledger_patterns

if settings.DEBUG:  # Serve media locally in development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
