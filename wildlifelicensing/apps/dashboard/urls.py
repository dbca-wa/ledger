from django.conf.urls import url

from . import views

urlpatterns = [
    url('^dashboard/?$', views.DashboardQuickView.as_view(), name='quick'),
    url('^dashboard/tables/?', views.DashboardTableView.as_view(), name='tables')
	url(r'^verification/(?P<token>[^/]+)/$', views.VerificationView.as_view(), name='verification'),
]
