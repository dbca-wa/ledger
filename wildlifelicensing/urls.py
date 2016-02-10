from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm

from wildlifelicensing.apps.accounts.urls import urlpatterns as accounts_urls

urlpattern = [
    url(r'^$', TemplateView.as_view(template_name="index.html"), {'form': AuthenticationForm}, name='home'),
    url(r'^accounts/', include(accounts_urls))
]
