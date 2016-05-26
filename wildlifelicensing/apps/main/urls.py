from django.conf.urls import url

from .views import (
        ListProfilesView, CreateProfilesView, EditProfilesView, DeleteProfileView,
        IdentificationView,
        EditAccountView,
		SearchCustomersView,
        ListDocumentView,EditDocumentView,CreateDocumentView,DeleteDocumentView
)


urlpatterns = [
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
]
