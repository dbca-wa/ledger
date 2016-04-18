from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^dashboard/?$', views.DashBoardRoutingView.as_view(), name='home'),
    url(r'^dashboard/customer/?$', views.DashboardCustomerTreeView.as_view(), name='tree_customer'),
    url(r'^dashboard/officer/?$', views.DashboardOfficerTreeView.as_view(), name='tree_officer'),
    url(r'^dashboard/tables/officer/?', views.DashboardTableOfficerView.as_view(), name='tables_officer'),
    url(r'^dashboard/tables/customer/?', views.DashboardTableCustomerView.as_view(), name='tables_customer'),
    url(r'^dashboard/tables/assessor/?', views.DashboardTableAssessorView.as_view(), name='tables_assessor'),
    url(r'^dashboard/data/applications/officer/?', views.ApplicationDataTableOfficerView.as_view(),
        name='applications_data_officer'),
    url(r'^dashboard/data/applications/customer/?', views.ApplicationDataTableCustomerView.as_view(),
        name='applications_data_customer'),
    url(r'^dashboard/data/applications/assessor/?', views.ApplicationDataTableCustomerView.as_view(),
        name='applications_data_assessor'),
]
