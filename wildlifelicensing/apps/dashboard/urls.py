from django.conf.urls import url

from .views import DashboardQuickView, DashboardTableView

urlpatterns = [
    url('^dashboard/?$', DashboardQuickView.as_view(), name='quick'),
    url('^dashboard/tables/?', DashboardTableView.as_view(), name='tables')
]
