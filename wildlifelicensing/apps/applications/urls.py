from django.conf.urls import url

from wildlifelicensing.apps.applications.views.entry import SelectLicenceTypeView, CheckIdentityRequiredView, CreateSelectPersonaView, \
    EnterDetailsView, PreviewView

from wildlifelicensing.apps.applications.views.process import ProcessView, ListOfficersView, AssignOfficerView

urlpatterns = [
    url('^select-licence-type$', SelectLicenceTypeView.as_view(), name='select_licence_type'),
    url('^([\w-]+)/check_identity/$', CheckIdentityRequiredView.as_view(), name='check_identity'),
    url('^([\w-]+)/persona/$', CreateSelectPersonaView.as_view(), name='create_select_persona'),
    url('^([\w-]+)/persona/([0-9]+)/$', CreateSelectPersonaView.as_view(), name='create_select_persona_existing_application'),
    url('^([\w-]+)/enter-details/$', EnterDetailsView.as_view(), name='enter_details'),
    url('^([\w-]+)/enter-details/([0-9]+)/$', EnterDetailsView.as_view(), name='enter_details'),
    url('^([\w-]+)/enter-details/([0-9]+)/$', EnterDetailsView.as_view(), name='enter_details_existing_application'),
    url('^([\w-]+)/preview/$', PreviewView.as_view(), name='preview'),
    url('^([\w-]+)/preview/([0-9]+)/$', PreviewView.as_view(), name='preview'),

    # process
    url(r'^process/(?P<id>[\w-]+)', ProcessView.as_view(), name='process'),
    url('^list_officers/$', ListOfficersView.as_view(), name='list_officers'),
    url('^list_officers/([0-9]+)/$', ListOfficersView.as_view(), name='list_officers'),
    url('^assign_officer/$', AssignOfficerView.as_view(), name='assign_officer'),
]
