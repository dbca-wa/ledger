from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from ledger.accounts import views
from ledger.accounts.api import UserReportView,UserAccountsList,UserAccountsLogsList

api_patterns = [
    url(r'api/report/duplicate_identity$', UserReportView.as_view(),name='ledger-user-report'),
    url(r'api/account/list$', UserAccountsList.as_view(),name='ledger-user-account'),
    url(r'api/account/logs/(?P<pk>\d+)$', UserAccountsLogsList.as_view(),name='ledger-user-account-logs'),
]

urlpatterns = [
    # url(r'^$', views.home, name='home'),
    url(r'^done/$', views.done, name='done'),
    url(r'^validation-sent/$', views.validation_sent, name='validation_sent'),
    url(r'^login-retry/$', views.login_retry, name='login_retry'),
    url(r'^login-expired/$', views.login_expired, name='login_expired'),
    url(r'^token-login/(?P<token>[^/]+)/(?P<email>[^/]+)/$', views.token_login, name='token_login'),
    url(r'^logout/', views.logout, name='logout'),
    url(r'^firsttime/', views.first_time, name='first_time'),
    url(r'accounts/', include(api_patterns)),
    url(r'account-management/(?P<pk>\d+)/change/$', views.AccountChange.as_view(), name='account_management_change'),    
    url(r'account-management/', views.AccountManagement.as_view(), name='account_management')
    
    
]
