from django.conf.urls import url, include

from wildlifelicensing.admin import wildlife_licensing_admin_site
from wildlifelicensing.apps.dashboard.views import DashBoardRoutingView
from wildlifelicensing.apps.dashboard.forms import LoginForm
from ledger.urls import urlpatterns as ledger_patterns

urlpatterns = [
    url(r'^admin/', wildlife_licensing_admin_site.urls),
    url(r'^$', DashBoardRoutingView.as_view(), {'form': LoginForm}, name='home'),
    url(r'', include('wildlifelicensing.apps.dashboard.urls', namespace='dashboard')),
    url(r'^applications/', include('wildlifelicensing.apps.applications.urls', namespace='applications')),
] + ledger_patterns
