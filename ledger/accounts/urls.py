from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views

from ledger.accounts import views
from ledger.accounts.api import UserReportView,UserAccountsList,UserAccountsLogsList

app_name = 'ledger.accounts'

api_patterns = [
    re_path(r'api/report/duplicate_identity$', UserReportView.as_view(),name='ledger-user-report'),
    re_path(r'api/account/list$', UserAccountsList.as_view(),name='ledger-user-account'),
    re_path(r'api/account/logs/(?P<pk>\d+)$', UserAccountsLogsList.as_view(),name='ledger-user-account-logs'),
]

urlpatterns = [
    # url(r'^$', views.home, name='home'),
    re_path(r'^done/$', views.done, name='done'),
    re_path(r'^validation-sent/$', views.validation_sent, name='validation_sent'),
    re_path(r'^login-retry/$', views.login_retry, name='login_retry'),
    re_path(r'^login-expired/$', views.login_expired, name='login_expired'),
    re_path(r'^token-login/(?P<token>[^/]+)/(?P<email>[^/]+)/$', views.token_login, name='token_login'),
    re_path(r'^logout/', views.logout, name='logout'),
    re_path(r'^firsttime/', views.first_time, name='first_time'),
    re_path(r'accounts/', include(api_patterns)),
    re_path(r'account-management/create/', views.AccountCreate.as_view(), name='account_management_create'),  
    re_path(r'account-management/(?P<pk>\d+)/change/$', views.AccountChange.as_view(), name='account_management_change'),    
    re_path(r'account-management/', views.AccountManagement.as_view(), name='account_management')
]
