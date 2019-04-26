from django.core.management.base import BaseCommand
from django.utils import timezone
from mooring.models import lotusnotesextract, RegisteredVessels
import json

from datetime import timedelta

class Command(BaseCommand):
    help = 'Take extract from lotus notes and merge from 7 vessels per line into 1 single record in RegisteredVessels model.'

    def handle(self, *args, **options):
        # Get all the new vessels information from JSON file.
        regos = json.load(open('dump_regos.json', 'r'))
        view = json.load(open('dump_view.json', 'r'))

        rego_list_to_add = []
        rego_list_to_keep = []

        for record in view:
            # Field names in list format.
            fields = ["DoTRego"]
            for i in range(1,6):
                reg = fields[0] + str(i)
                # Checking if the vessel rego is anything from 0 - 00000000.
                # These exist in Lotus Notes, from what has been manually checked all subsequent fields are empty.
                # Therefore we want to ignore anything with an integer value less than 1, just to clean up.
                rego_as_int = 1
                try:
                    rego_as_int = int(record[reg])
                except:
                    pass
                # Ignore records that are empty, have no rego etc. If they have a valid rego continue.
                if record[reg] is not None and not record[reg] == 'None' and not record[reg] == 'NoVessel' and not record[reg] == '' and not record[reg] == 'N/A' and not record[reg] == '?????' and not rego_as_int < 1:
                    # Rego can be added to the list.
                    rego_list_to_add.append(record[reg])


        for record in regos:
            # Field names in list format.
            fields = ["DoTRego", "TotLength", "Draft", "Beam", "Tonnage", "StickerLNo", "StickerAuNo", "StickerAnNo"]
            for i in range(1,8):
                reg = fields[0] + str(i)
                # Checking if the vessel rego is anything from 0 - 0000000.
                # These exist in Lotus Notes, from what has been manually checked all subsequent fields are empty.
                # Therefore we want to ignore anything with an integer value less than 1, just to clean up.
                rego_as_int = 1
                try:
                    rego_as_int = int(record[reg])
                except:
                    pass
                # Ignore records that are empty, have no rego etc. If they have a valid rego continue.
                if record[reg] is not None and not record[reg] == 'None' and not record[reg] == 'NoVessel' and not record[reg] == '' and not record[reg] == 'N/A' and not record[reg] == '?????' and not rego_as_int < 1:
                    if record[reg] in rego_list_to_add:
                        # Spare checking back over the array again at the end, we create a list of those valid regos for removing those not in the list later.
                        rego_list_to_keep.append(record[reg])
                        # Set the field names, selecting the correct value from the list then adding the iterator value.
                        size = fields[1] + str(i)
                        draft = fields[2] + str(i)
                        beam = fields[3] + str(i)
                        weight = fields[4] + str(i)
                        stickerl = fields[5] + str(i)
                        stickerau = fields[6] + str(i)
                        stickeran = fields[7] + str(i)
                        # Inserting a line with a None or null value will raise error.
                        # We always want to pass something to have cleaner code for creation.
                        # So if None/null, set to default 0.00.
                        if record[size] == None:
                            record[size] = 0.00
                        if record[draft] == None:
                            record[draft] = 0.00
                        if record[beam] == None:
                            record[beam] = 0.00
                        if record[weight] == None:
                            record[weight] = 0.00

                        # Checking for vessels with same rego.
                        exists = RegisteredVessels.objects.filter(rego_no=record[reg])
                        # If a vessel is already existing with the same rego, do some comparisons.
                        # Otherwise just create a new vessel object and save it.
                        if exists:
                            # Check if current record we are reading in from JSON has sticker values.
                            if record[stickerl] or record[stickerau] or record[stickeran]:
                                # Then check if the found existing rego does not have these values.
                                if not exists[0].sticker_l or not exists[0].sticker_au or not exists[0].sticker_an:
                                    # New one is definitely better to have in.
                                    ves = RegisteredVessels.objects.create(rego_no=record[reg], vessel_size=record[size], vessel_draft=record[draft], vessel_beam=record[beam], vessel_weight=record[weight], sticker_l=record[stickerl], sticker_au=record[stickerau], sticker_an=record[stickeran])
                                    exists[0].delete()
                                else:
                                    # Both old and new have stickers. Keep old.
                                    ves = exists[0]
                                    pass
                            else:
                                # Check if the found record has stickers (in this case the JSON record does not).
                                if exists[0].sticker_l or exists[0].sticker_au or exists[0].sticker_an:
                                    # We need to keep the old.
                                    ves = exists[0]
                                    pass
                                else:
                                    # Neither have stickers, check if there are differences in measurements.
                                    # If the existing record has a higher value for any of the following, keep that record.
                                    # Otherwise remove it and add the new.
                                    if exists[0].vessel_size > record[size] or exists[0].vessel_draft > record[draft] or exists[0].vessel_beam > record[beam] or exists[0].vessel_weight > record[weight]:
                                        ves = exists[0]
                                    else:
                                        ves = RegisteredVessels.objects.create(rego_no=record[reg], vessel_size=record[size], vessel_draft=record[draft], vessel_beam=record[beam], vessel_weight=record[weight], sticker_l=record[stickerl], sticker_au=record[stickerau], sticker_an=record[stickeran])
                                        exists[0].delete()
                        else:
                            ves = RegisteredVessels.objects.create(rego_no=record[reg], vessel_size=record[size], vessel_draft=record[draft], vessel_beam=record[beam], vessel_weight=record[weight], sticker_l=record[stickerl], sticker_au=record[stickerau], sticker_an=record[stickeran])

        # Those vessels that were not in the JSON from Lotus Notes but are existing in the moorings DB
        # need to be removed. Check for those by getting all excluding those that have been checked
        # from JSON. Then delete the ones that were not in JSON but are in DB.
        excluded_vessels = RegisteredVessels.objects.exclude(rego_no__in=rego_list)
        excluded_vessels.delete()