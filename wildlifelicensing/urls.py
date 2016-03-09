from django.conf.urls import url, include
from django.contrib import admin

from wildlifelicensing.apps.accounts.forms import LoginForm
from wildlifelicensing.apps.dashboard.views import DashBoardRoutingView

from wildlifelicensing.admin import wildlife_licensing_admin_site

urlpatterns = [
    url(r'^admin/', wildlife_licensing_admin_site.urls),
    url(r'^$', DashBoardRoutingView.as_view(), {'form': LoginForm}, name='home'),
    url(r'^accounts/', include('wildlifelicensing.apps.accounts.urls', namespace='accounts')),
    url(r'', include('wildlifelicensing.apps.dashboard.urls', namespace='dashboard')),
    url(r'', include('wildlifelicensing.apps.applications.urls', namespace='applications')),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
