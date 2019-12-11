from django.conf.urls import url

from wildlifelicensing.apps.dashboard.views import base, officer, customer, assessor

urlpatterns = [
    url(r'^dashboard/?$', base.DashBoardRoutingView.as_view(), name='home'),
    url(r'^dashboard/officer/?$', officer.DashboardOfficerTreeView.as_view(), name='tree_officer'),
    url(r'^dashboard/tables/customer/?$', customer.TableCustomerView.as_view(), name='tables_customer'),
    url(r'^dashboard/tables/assessor/?$', assessor.TableAssessorView.as_view(), name='tables_assessor'),

    # Applications
    url(r'^dashboard/tables/applications/officer/?$', officer.TablesApplicationsOfficerView.as_view(),
        name='tables_applications_officer'),
    url(r'^dashboard/data/applications/officer/?$', officer.DataTableApplicationsOfficerView.as_view(),
        name='data_application_officer'),
    url(r'^dashboard/tables/officer/onbehalf/?$', officer.TablesOfficerOnBehalfView.as_view(),
        name='tables_officer_onbehalf'),
    url(r'^dashboard/data/applications/officer/onbehalf/?$', officer.DataTableApplicationsOfficerOnBehalfView.as_view(),
        name='data_application_officer_onbehalf'),
    url(r'^dashboard/data/applications/customer/?$', customer.DataTableApplicationCustomerView.as_view(),
        name='data_application_customer'),
    url(r'^dashboard/data/applications/assessor/?$', assessor.DataTableApplicationAssessorView.as_view(),
        name='data_application_assessor'),

    # Licences
    url(r'^dashboard/tables/licences/officer/?$', officer.TablesLicencesOfficerView.as_view(),
        name='tables_licences_officer'),
    url(r'^dashboard/data/licences/officer/?$', officer.DataTableLicencesOfficerView.as_view(),
        name='data_licences_officer'),
    url(r'^dashboard/data/licences/customer/?$', customer.DataTableLicencesCustomerView.as_view(),
        name='data_licences_customer'),
    url(r'^dashboard/bulk-licence-renewal-pdf/?$', officer.BulkLicenceRenewalPDFView.as_view(),
        name='bulk_licence_renewal_pdf'),

    # Returns
    url(r'^dashboard/tables/returns/officer/?$', officer.TablesReturnsOfficerView.as_view(),
        name='tables_returns_officer'),
    url(r'^dashboard/data/returns/officer/?$', officer.DataTableReturnsOfficerView.as_view(),
        name='data_returns_officer'),
    url(r'^dashboard/data/returns/officer/onbehalf/?$', officer.DataTableReturnsOfficerOnBehalfView.as_view(),
        name='data_returns_officer_onbehalf'),
    url(r'^dashboard/data/returns/customer/?$', customer.DataTableReturnsCustomerView.as_view(),
        name='data_returns_customer'),
]
