from django.conf.urls import patterns, url
from django.contrib.auth import views as auth_views

urlpatterns = patterns('customers',
    url(r'^$', 'views.home', name='home'),
    url(r'^done/$', 'views.done', name='done'),
    url(r'^login-form/$', 'views.login_form', name='login_form'),
    url(r'^validation-sent/$', 'views.validation_sent',
        name='validation_sent'),
    url(r'^token-login/(?P<token>[^/]+)/$', 'views.token_login',
        name='token_login'),
    url('^logout/', auth_views.logout, {'next_page': 'customers:home'}, name='logout'),

)
