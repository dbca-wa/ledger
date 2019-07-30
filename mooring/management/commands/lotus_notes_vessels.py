from django.core.management.base import BaseCommand
from django.utils import timezone
from mooring.models import RegisteredVessels
from mooring.emails import send_registered_vessels_email
from datetime import datetime
import json

from datetime import timedelta

class Command(BaseCommand):
    help = 'Take extract from lotus notes and merge from 7 vessels per line into 1 single record in RegisteredVessels model.'

    def add_arguments(self, parser):
        parser.add_argument('path')

    def handle(self, *args, **options):
        try:
            # Get all the new vessels information from JSON file.
            if options['path']:
                regos_path = options['path'] + 'dump_regos.json'
                view_path = options['path'] + 'dump_view.json'
                regos = json.load(open(regos_path, 'r'))
                view = json.load(open(view_path, 'r'))
            else:
                regos = json.load(open('dump_regos.json', 'r'))
                view = json.load(open('dump_view.json', 'r'))

            rego_list_to_add = []
            rego_list_to_keep = []
            rego_info_from_dump = []


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


            # Field names in list format.
            fields = ["DoTRego", "RegLength", "Draft", "Beam", "Tonnage", "StickerLNo", "StickerAuNo", "StickerAnNo"]

            for record in regos:
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

                            # Create a dict of the vessel
                            vessel = {fields[0] : record[reg], fields[1]: record[size], fields[2]: record[draft], fields[3]: record[beam], fields[4]: record[weight], fields[5]: record[stickerl], fields[6]: record[stickerau], fields[7]: record[stickeran]}
                            # Get the index of the vessel in the rego_info_from_dump.
                            # If it's not None, we already have an existing record for this rego.
                            # Therefore update the values if they are larger/exist.
                            index = next((index for (index, d) in enumerate(rego_info_from_dump) if d[fields[0]] == record[reg]), None)
                            if index is not None:
                                if rego_info_from_dump[index][fields[1]] < record[size]:
                                    rego_info_from_dump[index][fields[1]] = record[size]
                                if rego_info_from_dump[index][fields[2]] < record[draft]:
                                    rego_info_from_dump[index][fields[2]] = record[draft]
                                if rego_info_from_dump[index][fields[3]] < record[beam]:
                                    rego_info_from_dump[index][fields[3]] = record[beam]
                                if rego_info_from_dump[index][fields[4]] < record[weight]:
                                    rego_info_from_dump[index][fields[4]] = record[weight]
                                if not rego_info_from_dump[index][fields[5]] and record[stickerl]:
                                    rego_info_from_dump[index][fields[5]] = record[stickerl]
                                if not rego_info_from_dump[index][fields[6]] and record[stickerau]:
                                    rego_info_from_dump[index][fields[6]] = record[stickerau]
                                if not rego_info_from_dump[index][fields[7]] and record[stickeran]:
                                    rego_info_from_dump[index][fields[7]] = record[stickeran]
                            else:
                                rego_info_from_dump.append(vessel)


            # Now iterate through, checking against what is in the database.
            for record in rego_info_from_dump:
                # Spare checking back over the array again at the end, we create a list of those valid regos for removing those not in the list later.
                rego_list_to_keep.append(record[fields[0]])
                # Checking for vessels with same rego.
                exists = RegisteredVessels.objects.filter(rego_no=record[fields[0]])
                # If a vessel is already existing with the same rego, do some comparisons and update those values.
                # Otherwise just create a new vessel object and save it.
                if exists:
                    if exists[0].vessel_size < record[fields[1]]:
                        exists[0].vessel_size = record[fields[1]]
                    if exists[0].vessel_draft < record[fields[2]]:
                        exists[0].vessel_draft = record[fields[2]]
                    if exists[0].vessel_beam < record[fields[3]]:
                        exists[0].vessel_beam = record[fields[3]]
                    if exists[0].vessel_weight < record[fields[4]]:
                        exists[0].vessel_weight = record[fields[4]]
                    exists[0].sticker_l = record[fields[5]]    
                    exists[0].sticker_au = record[fields[6]]
                    exists[0].sticker_an = record[fields[7]]

                    exists[0].save()
                else:
                    ves = RegisteredVessels.objects.create(rego_no=record[fields[0]], vessel_size=record[fields[1]], vessel_draft=record[fields[2]], vessel_beam=record[fields[3]], vessel_weight=record[fields[4]], sticker_l=record[fields[5]], sticker_au=record[fields[6]], sticker_an=record[fields[7]])

            # Those vessels that were not in the JSON from Lotus Notes but are existing in the moorings DB
            # need to be removed. Check for those by getting all excluding those that have been checked
            # from JSON. Then delete the ones that were not in JSON but are in DB.
            excluded_vessels = RegisteredVessels.objects.exclude(rego_no__in=rego_list_to_keep)
            excluded_vessels.delete()

            #Send success email
            total = RegisteredVessels.objects.all().count()
            time = datetime.now()
            content = "Extract has completed successfully.\n{} vessels total.\nFinished run at {}.".format(total, time)
            send_registered_vessels_email(content)
        except Exception as e:
            print (e)
            #Send fail email
            content = "Extract has failed.\nError message: {}".format(e)
            send_registered_vessels_email(content)
