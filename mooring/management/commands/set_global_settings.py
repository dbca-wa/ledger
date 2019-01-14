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
                if not GlobalSettings.objects.get(mooring_group=group, key=i):
                    new = GlobalSettings.objects.create(mooring_group=group, key=i, value=25)