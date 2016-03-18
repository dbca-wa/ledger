from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^dashboard/?$', views.DashboardQuickView.as_view(), name='quick'),
    url(r'^dashboard/tables/?', views.DashboardTableView.as_view(), name='tables'),
    url('^dashboard/data/applications/?', views.ApplicationDataTableView.as_view(), name='applications_data'),
    url(r'^verification/(?P<token>[^/]+)/$', views.VerificationView.as_view(), name='verification'),
]
