from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^dashboard/?$', views.DashBoardRoutingView.as_view(), name='home'),
    url(r'^dashboard/customer/?$', views.DashboardCustomerTreeView.as_view(), name='tree_customer'),
    url(r'^dashboard/officer/?$', views.DashboardOfficerTreeView.as_view(), name='tree_officer'),
    url(r'^dashboard/tables/?', views.DashboardTableView.as_view(), name='tables'),
    url('^dashboard/data/applications/?', views.ApplicationDataTableView.as_view(), name='applications_data'),
]
