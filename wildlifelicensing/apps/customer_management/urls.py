from django.conf.urls import url

from wildlifelicensing.apps.customer_management.views.customer import CustomerLookupView, \
    EditDetailsView, EditProfileView
from wildlifelicensing.apps.customer_management.views.tables import DataTableApplicationView,\
    DataTableLicencesView, DataTableReturnsView


urlpatterns = [
    url('^$', CustomerLookupView.as_view(), name='customer_lookup'),
    url('^([0-9]+)/$', CustomerLookupView.as_view(), name='customer_lookup'),
    url('^([0-9]+)/edit_details/$', EditDetailsView.as_view(), name='edit_customer_details'),
    url('^([0-9]+)/edit_profile/$', EditProfileView.as_view(), name='edit_customer_profile'),
    url('^([0-9]+)/edit_profile/([0-9]+)/$', EditProfileView.as_view(), name='edit_customer_profile'),

    # tables
    url(r'^data/applications/([0-9]+)/?$', DataTableApplicationView.as_view(), name='data_applications'),
    url(r'^data/licences/([0-9]+)/?$', DataTableLicencesView.as_view(), name='data_licences'),
    url(r'^data/returns/([0-9]+)/?$', DataTableReturnsView.as_view(), name='data_returns')
]
