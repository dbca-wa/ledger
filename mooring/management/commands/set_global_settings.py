from django.core.management.base import BaseCommand
from django.utils import timezone
from mooring.models import GlobalSettings, MooringAreaGroup
import json

from datetime import timedelta

class Command(BaseCommand):
    help = 'Create all required GlobalSettings objects.'

    def handle(self, *args, **options):
        groups = MooringAreaGroup.objects.all()

        for group in groups:
            for i in range(15):
                if GlobalSettings.objects.filter(mooring_group=group, key=i).count() == 0:
                    if i == 0:
                        value = 0 
                    if i == 1:
                        value = 31
                    if i == 2:
                        value = 180
                    if i in (3,6,9,12):
                        value = 20
                    if i in (4,7,10,13):
                        value = 50
                    if i in (5,8,11,14):
                        value = 100
                    
                    new = GlobalSettings.objects.create(mooring_group=group, key=i, value=value)
