from django.conf.urls import url, include
from django.contrib import admin

from wildlifelicensing.apps.accounts.forms import LoginForm
from wildlifelicensing.apps.accounts.views import DashBoardView

from wildlifelicensing.admin import wildlife_licensing_admin_site

urlpatterns = [
    url(r'^admin/', wildlife_licensing_admin_site.urls),
    url(r'^$', DashBoardView.as_view(), {'form': LoginForm}, name='home'),
    url(r'^accounts/', include('wildlifelicensing.apps.accounts.urls', namespace='accounts')),
    url(r'^customers/', include('wildlifelicensing.apps.customers.urls', namespace='customers')),
    url(r'^officers/', include('wildlifelicensing.apps.officers.urls', namespace='officers')),
    url(r'^applications/', include('wildlifelicensing.apps.applications.urls', namespace='applications')),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
