from django.conf.urls import url, include
from django.contrib import admin

from wildlifelicensing.apps.accounts.forms import LoginForm
from wildlifelicensing.apps.accounts.views import DashBoardView

from wildlifelicensing.admin import wildlife_licensing_admin_site
from wildlifelicensing.apps.dashboard.views import DashBoardView
from wildlifelicensing.apps.dashboard.forms import LoginForm
from ledger.urls import urlpatterns as ledger_patterns
from wildlifelicensing.admin import admin_site
urlpatterns = [
    url(r'^admin/', wildlife_licensing_admin_site.urls),
    url(r'^$', DashBoardRoutingView.as_view(), {'form': LoginForm}, name='home'),
    url(r'', include('wildlifelicensing.apps.dashboard.urls', namespace='dashboard')),
    url(r'', include('wildlifelicensing.apps.applications.urls', namespace='applications')),
] + ledger_patterns
