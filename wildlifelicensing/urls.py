from django.conf.urls import url, include, static
from django.conf import settings

from wildlifelicensing.admin import wildlife_licensing_admin_site
from wildlifelicensing.apps.dashboard.views.base import DashBoardRoutingView
from ledger.urls import urlpatterns as ledger_patterns

urlpatterns = [
    url(r'^admin/', wildlife_licensing_admin_site.urls),
    url(r'^$', DashBoardRoutingView.as_view(), name='wl_home'),
    url(r'', include('wildlifelicensing.apps.main.urls', namespace='wl_main')),
    url(r'', include('wildlifelicensing.apps.dashboard.urls', namespace='wl_dashboard')),
    url(r'^applications/', include('wildlifelicensing.apps.applications.urls', namespace='wl_applications')),
    url(r'^customer_management/', include('wildlifelicensing.apps.customer_management.urls', namespace='wl_customer_management')),
    url(r'^reports/', include('wildlifelicensing.apps.reports.urls', namespace='wl_reports')),
    url(r'^returns/', include('wildlifelicensing.apps.returns.urls', namespace='wl_returns')),
    url(r'^payments/', include('wildlifelicensing.apps.payments.urls', namespace='wl_payments')),
] + ledger_patterns

if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
