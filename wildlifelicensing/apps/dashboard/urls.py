from django.conf.urls import url

from wildlifelicensing.apps.dashboard import views

urlpatterns = [
    url(r'^dashboard/?$', views.DashBoardRoutingView.as_view(), name='home'),
    url(r'^dashboard/officer/?$', views.DashboardOfficerTreeView.as_view(), name='tree_officer'),
    url(r'^dashboard/tables/customer/?$', views.TableCustomerView.as_view(), name='tables_customer'),
    url(r'^dashboard/tables/assessor/?$', views.TableAssessorView.as_view(), name='tables_assessor'),
    # url(r'^dashboard/tables/assessor/?', views.TableAssessorView.as_view(), name='assessor'),

    # Applications
    url(r'^dashboard/tables/applications/officer/?$', views.TableApplicationsOfficerView.as_view(),
        name='tables_applications_officer'),
    url(r'^dashboard/data/applications/officer/?$', views.DataTableApplicationsOfficerView.as_view(),
        name='data_application_officer'),

    url(r'^dashboard/tables/applications/officer/onbehalf/?$', views.TableApplicationsOfficerOnBehalfView.as_view(),
        name='tables_applications_officer_onbehalf'),
    url(r'^dashboard/data/applications/officer/onbehalf/?$', views.DataTableApplicationsOfficerOnBehalfView.as_view(),
        name='data_application_officer_onbehalf'),

    url(r'^dashboard/data/applications/customer/?$', views.DataTableApplicationCustomerView.as_view(),
        name='data_application_customer'),
    url(r'^dashboard/data/applications/assessor/?$', views.DataTableApplicationAssessorView.as_view(),
        name='data_application_assessor'),

    # Licences
    url(r'^dashboard/tables/licences/officer/?$', views.TableLicencesOfficerView.as_view(),
        name='tables_licences_officer'),
    url(r'^dashboard/data/licences/officer/?$', views.DataTableLicencesOfficerView.as_view(),
        name='data_licences_officer'),
    url(r'^dashboard/data/licences/customer/?$', views.DataTableLicencesCustomerView.as_view(),
        name='data_licences_customer'),

    # Returns
    url(r'^dashboard/tables/returns/officer/?$', views.TableReturnsOfficerView.as_view(),
        name='tables_returns_officer'),
    url(r'^dashboard/data/returns/officer/?$', views.DataTableReturnsOfficerView.as_view(),
        name='data_returns_officer'),
    url(r'^dashboard/data/returns/customer/?$', views.DataTableReturnsCustomerView.as_view(),
        name='data_returns_customer'),
]
