from django.conf.urls import url

from views import SelectLicenceTypeView, CreateSelectPersonaView, EnterDetails, PreviewView

urlpatterns = [
    url('^select-licence-type$', SelectLicenceTypeView.as_view(), name='select_licence_type'),
    url('^([\w-]+)/persona/$', CreateSelectPersonaView.as_view(), name='create_select_persona'),
    url('^([\w-]+)/enter-details/$', EnterDetails.as_view(), name='enter_details'),
    url('^([\w-]+)/preview/$', PreviewView.as_view(), name='preview'),
]
