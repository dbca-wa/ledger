from django import forms

from openpyxl import load_workbook

from models import Species, SpeciesFile

class SpeciesFileForm(forms.ModelForm):
    class Meta:
        model = SpeciesFile
        exclude = []

    def clean(self):
        species_ws = load_workbook(self.cleaned_data.get("file", False)).active
        col_max = species_ws.get_highest_row()
        species_list = [cell.value for (cell,) in list(species_ws.get_squared_range(1, 1, 1, col_max))]
    
        invalid_species = []
    
        for species in species_list:
            # Remove multiple spaces, tabs, newlines, leading/trailing spaces.
            species = ' '.join(species.split()).capitalize()
            
            if Species.objects.filter(species_name=species).count() == 1:
                continue
            
            species_components = species.split(' ', 2)

            # At this point, we have uncertainty about species (but still might match genus).
            if species_components and len(species_components) == 1:  # Only supplied genus.
                invalid_species.append(species)
                continue
   
            # No match on exact species name; try "Genus sp."
            if species_components[1] != 'sp.':
                invalid_species.append(species)
                continue

        if len(invalid_species) > 0:
            raise forms.ValidationError('The following species are invalid or not in the system database: <p>- ' + '</p><p>- '.join(invalid_species) + '</p>')

        return self.cleaned_data
