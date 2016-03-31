from django.conf.urls import url

from wildlifelicensing.apps.applications.views.entry import SelectLicenceTypeView, CreateSelectPersonaView, EnterDetailsView, PreviewView

urlpatterns = [
    url('^select-licence-type$', SelectLicenceTypeView.as_view(), name='select_licence_type'),
    url('^([\w-]+)/persona/$', CreateSelectPersonaView.as_view(), name='create_select_persona'),
    url('^([\w-]+)/persona/([0-9]+)/$', CreateSelectPersonaView.as_view(), name='create_select_persona_existing_application'),
    url('^([\w-]+)/enter-details/$', EnterDetailsView.as_view(), name='enter_details'),
    url('^([\w-]+)/enter-details/([0-9]+)/$', EnterDetailsView.as_view(), name='enter_details'),
    url('^([\w-]+)/enter-details/([0-9]+)/$', EnterDetailsView.as_view(), name='enter_details_existing_application'),
    url('^([\w-]+)/preview/$', PreviewView.as_view(), name='preview'),
    url('^([\w-]+)/preview/([0-9]+)/$', PreviewView.as_view(), name='preview'),
]
