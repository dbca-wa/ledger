from django.conf.urls import url

from views import ListPersonasView, CreatePersonasView, EditPersonasView


urlpatterns = [
    url('^personas/$', ListPersonasView.as_view(), name='list_personas'),
    url('^personas/create/$', CreatePersonasView.as_view(), name='create_persona'),
    url('^personas/edit/([0-9]+)/$', EditPersonasView.as_view(), name='edit_persona'),
]
