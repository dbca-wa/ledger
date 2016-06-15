from django.conf.urls import url

from wildlifelicensing.apps.customer_management.views.management import CustomerLookupView, ViewCustomerView, \
    EditDetailsView, EditProfileView
from wildlifelicensing.apps.customer_management.views.tables import DataTableApplicationView,\
    DataTableLicencesView, DataTableReturnsView


urlpatterns = [
    url('^lookup_customer/$', CustomerLookupView.as_view(), name='lookup_customer'),
    url('^view_person/([0-9]+)/$', ViewCustomerView.as_view(), name='view_customer'),
    url('^view_person/([0-9]+)/edit_details/$', EditDetailsView.as_view(), name='edit_customer_details'),
    url('^view_person/([0-9]+)/edit_profile/$', EditProfileView.as_view(), name='edit_customer_profile'),
    url('^view_person/([0-9]+)/edit_profile/([0-9]+)/$', EditProfileView.as_view(), name='edit_customer_profile'),

    # tables
    url(r'^data/applications/([0-9]+)/?$', DataTableApplicationView.as_view(), name='data_applications'),
    url(r'^data/licences/([0-9]+)/?$', DataTableLicencesView.as_view(), name='data_licences'),
    url(r'^data/returns/([0-9]+)/?$', DataTableReturnsView.as_view(), name='data_returns')
]
