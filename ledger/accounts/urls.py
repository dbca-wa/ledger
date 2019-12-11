from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views

from ledger.accounts import views
from ledger.accounts.api import UserReportView

api_patterns = [
    path('api/report/duplicate_identity', UserReportView.as_view(),name='ledger-user-report'),
]

urlpatterns = [
    path('', views.home, name='home'),
    path('done/', views.done, name='done'),
    path('validation-sent/', views.validation_sent, name='validation_sent'),
    path('login-retry/', views.login_retry, name='login_retry'),
    path('login-expired/', views.login_expired, name='login_expired'),
    re_path(r'^token-login/(?P<token>[^/]+)/(?P<email>[^/]+)/$', views.token_login, name='token_login'),
    path('logout/', views.logout, name='logout'),
    path('firsttime/', views.first_time, name='first_time'),
    path('accounts/', include(api_patterns)),
]
