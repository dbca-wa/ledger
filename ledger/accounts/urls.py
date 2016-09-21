from django.conf.urls import patterns, url, include
from django.contrib.auth import views as auth_views

from ledger.accounts import views
from ledger.accounts.api import UserReportView

api_patterns = [
    url(r'api/report/duplicate_identity$', UserReportView.as_view(),name='ledger-user-report'),
]

urlpatterns = patterns('accounts',
    url(r'^$', views.home, name='home'),
    url(r'^done/$', views.done, name='done'),
    url(r'^validation-sent/$', views.validation_sent, name='validation_sent'),
    url(r'^token-login/(?P<token>[^/]+)/(?P<email>[^/]+)/$', views.token_login, name='token_login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^firsttime/', views.first_time, name='first_time'),
    url(r'accounts/', include(api_patterns)),
)
