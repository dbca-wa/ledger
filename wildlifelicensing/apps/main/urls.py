from django.conf.urls import url
from django.views.generic.base import TemplateView, RedirectView

from wildlifelicensing.apps.main.views import ListProfilesView, CreateProfilesView, EditProfilesView, \
    IdentificationView, EditAccountView, SearchCustomersView, LicenceRenewalPDFView, \
    CommunicationsLogListView, AddCommunicationsLogEntryView

urlpatterns = [
    url(r'contact-us/$', TemplateView.as_view(template_name="wl/contact_us.html"), name='contact_us'),
    url(r'further-information/$', RedirectView.as_view(url='https://www.dpaw.wa.gov.au/plants-and-animals/licences-and-authorities'),
        name='further_information'),

    url('^account/$', EditAccountView.as_view(), name='edit_account'),
    url('^search_customers/$', SearchCustomersView.as_view(), name='search_customers'),

    url('^profiles/$', ListProfilesView.as_view(), name='list_profiles'),
    url('^profiles/create/$', CreateProfilesView.as_view(), name='create_profile'),
    url('^profiles/edit/$', EditProfilesView.as_view(), name='edit_profile_prefix'),
    url('^profiles/edit/([0-9]+)/$', EditProfilesView.as_view(), name='edit_profile'),

    url('^identification/$', IdentificationView.as_view(), name='identification'),

    url('^licence-renewal-pdf/([0-9]+)/$', LicenceRenewalPDFView.as_view(), name='licence_renewal_pdf'),

    # general communications log
    url('^add-log-entry/([0-9]+)/$', AddCommunicationsLogEntryView.as_view(), name='add_log_entry'),
    url('^log-list/([0-9]+)/$', CommunicationsLogListView.as_view(), name='log_list')
]
