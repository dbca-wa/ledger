from django.urls import path, re_path, include
from .views import SpeciesNamesJSON

urlpatterns = [
    re_path(r'species_name', SpeciesNamesJSON.as_view(), name='species_names_json'),
]
