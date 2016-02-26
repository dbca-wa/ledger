from django.conf.urls import url, include
from django.contrib import admin

from wildlifelicensing.dashboard.forms import LoginForm
from wildlifelicensing.dashboard.views import DashBoardView

from wildlifelicensing.admin import admin_site

from ledger.urls import urlpatterns as ledger_patterns

urlpatterns = [
    url(r'^admin/', admin_site.urls),
    url(r'^$', DashBoardView.as_view(), {'form': LoginForm}, name='home'),
    url(r'^dashboard/', include('wildlifelicensing.dashboard.urls', namespace='dashboard')),
] + ledger_patterns
