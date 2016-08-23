from django.conf.urls import url
from django.views.generic.base import TemplateView, RedirectView


from wildlifelicensing.apps.main.views import ListProfilesView, CreateProfilesView, EditProfilesView, \
    DeleteProfileView, IdentificationView, EditAccountView, SearchCustomersView, ListDocumentView, \
    EditDocumentView, CreateDocumentView ,DeleteDocumentView, LicenceRenewalPDFView, \
    CommunicationsLogListView, AddCommunicationsLogEntryView, BulkLicenceRenewalPDFView


urlpatterns = [
    url(r'contact-us/$', TemplateView.as_view(template_name="wl/contact_us.html"), name='contact_us'),
    url(r'further-information/$', RedirectView.as_view(url='https://www.dpaw.wa.gov.au/plants-and-animals/licences-and-permits'),
        name='further_information'),

    url('^account/$', EditAccountView.as_view(), name='edit_account'),
    url('^search_customers/$', SearchCustomersView.as_view(), name='search_customers'),

    #url('^document/$', ListDocumentView.as_view(), name='list_documents'),
    #url('^document/create/$', CreateDocumentView.as_view(), name='create_document'),
    #url('^document/edit/(?P<id>[0-9]+)/$', EditDocumentView.as_view(), name='edit_document'),
    #url('^document/edit/$', EditDocumentView.as_view(), name='edit_document_prefix'),
    #url('^document/delete/(?P<id>[0-9]+)/$', DeleteDocumentView.as_view(), name='delete_document'),
    #url('^document/delete/$', DeleteDocumentView.as_view(), name='delete_document_prefix'),

    url('^profiles/$', ListProfilesView.as_view(), name='list_profiles'),
    url('^profiles/create/$', CreateProfilesView.as_view(), name='create_profile'),
    url('^profiles/edit/$', EditProfilesView.as_view(), name='edit_profile_prefix'),
    url('^profiles/edit/([0-9]+)/$', EditProfilesView.as_view(), name='edit_profile'),
    #url('^profiles/delete/(?P<id>[0-9]+)/$', DeleteProfileView.as_view(), name='delete_profile'),
    #url('^profiles/delete/$', DeleteProfileView.as_view(), name='delete_profile_prefix'),

    url('^identification/$', IdentificationView.as_view(), name='identification'),

    url('^licence-renewal-pdf/([0-9]+)/$', LicenceRenewalPDFView.as_view(), name='licence_renewal_pdf'),

    # general communications log
    url('^add-log-entry/([0-9]+)/$', AddCommunicationsLogEntryView.as_view(), name='add_log_entry'),
    url('^log-list/([0-9]+)/$', CommunicationsLogListView.as_view(), name='log_list')
]
