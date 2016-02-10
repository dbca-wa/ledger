from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import AuthenticationForm

urlpattern = [
    url('^login/', auth_views.login, {'template_name': 'index.html'}, name='login'),
    url(r'^$', TemplateView.as_view(template_name="index.html"), {'form': AuthenticationForm}),
]
