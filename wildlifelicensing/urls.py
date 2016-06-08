from django.conf.urls import url, include, static
from django.conf import settings

from wildlifelicensing.admin import wildlife_licensing_admin_site
from wildlifelicensing.apps.dashboard.views.base import DashBoardRoutingView
from ledger.urls import urlpatterns as ledger_patterns

urlpatterns = [
    url(r'^admin/', wildlife_licensing_admin_site.urls),
    url(r'^$', DashBoardRoutingView.as_view(), name='home'),
    url(r'', include('wildlifelicensing.apps.main.urls', namespace='main')),
    url(r'', include('wildlifelicensing.apps.dashboard.urls', namespace='dashboard')),
    url(r'^applications/', include('wildlifelicensing.apps.applications.urls', namespace='applications')),
    url(r'^returns/', include('wildlifelicensing.apps.returns.urls', namespace='returns')),
] + ledger_patterns

if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
