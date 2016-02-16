from django.conf.urls import url, include
from django.contrib import admin

from wildlifelicensing.apps.accounts.forms import LoginForm
from wildlifelicensing.apps.accounts.views import DashBoardView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', DashBoardView.as_view(), {'form': LoginForm}, name='home'),
    url(r'^accounts/', include('wildlifelicensing.apps.accounts.urls', namespace='accounts')),
    url(r'^applicants/', include('wildlifelicensing.apps.applicants.urls', namespace='applicants')),
    url(r'^officers/', include('wildlifelicensing.apps.officers.urls', namespace='officers')),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
