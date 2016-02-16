from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib.auth.forms import AuthenticationForm

urlpattern = [
    url(r'^$', TemplateView.as_view(template_name="index.html"), {'form': AuthenticationForm}, name='home'),
    url(r'^accounts/', include('wildlifelicensing.apps.accounts.urls')),
    url(r'^applicants/', include('wildlifelicensing.apps.applicants.urls', namespace='applicants')),
    url(r'^officers/', include('wildlifelicensing.apps.officers.urls', namespace='officers')),
]
