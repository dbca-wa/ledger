from django.conf.urls import url
from .views import SpeciesNamesJSON

urlpatterns = [
    url(r'species/$', SpeciesNamesJSON.as_view(), name='species_names_json'),
]
