import logging

from django.contrib import admin
from models import Species, SpeciesFile
from forms import SpeciesFileForm

logger = logging.getLogger(__name__)


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    readonly_fields = ['species_name', 'name_id', 'source']
    list_display = ['species_name', 'name_id', 'source']
    list_filter = ['source']
    search_fields = ['species_name', 'name_id']


@admin.register(SpeciesFile)
class SpeciesFileAdmin(admin.ModelAdmin):
    change_form_template = 'main/speciesfile_change_form.html'
    list_display = ['id', 'file', 'uploaded_date', 'validated']
    exclude = ['validated']
    form = SpeciesFileForm

    def save_model(self, request, obj, form, change):
        instance = form.save(commit=False)
        instance.validated = True
        instance.save()
        form.save_m2m()
        return instance
