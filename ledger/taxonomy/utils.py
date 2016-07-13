import os
from openpyxl import Workbook
from upload import utils_openpyxl
from species.models import Species


def species_names_to_excel(destination=None, force_update=False):
    """
    Create a excel workbook with all the species name dumped in the first column of the first worksheet.
    Calling this function will trigger an update of the species table from the herbie KMI web service if
    table is empty or the force_update=True
    :param destination: the destination path
    :param force_update: if true update the species table from the herbie KMI web service
    :return:
    """
    # update of the species table
    if force_update or Species.objects.count() == 0:
        Species.objects.update_herbie_hbvspecies()
    # export to excel
    if destination is None:
            destination = './local/species_names.xlsx'
    dir_ = os.path.dirname(destination)
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    wb = Workbook(write_only=True)
    ws = wb.create_sheet(title='Species')
    species_names = [species.species_name for species in Species.objects.all()]
    for name in species_names:
        ws.append([name])
    wb.save(destination)
    return destination
