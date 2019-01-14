from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import Group

from mooring.models import MooringAreaGroup

from datetime import timedelta

class Command(BaseCommand):
    help = 'Set auth groups.'

    def handle(self, *args, **options):
        if not Group.objects.filter(name="Mooring Admin").count() > 0:
            Group.objects.create(name="Mooring Admin")
        if not Group.objects.filter(name="Mooring Inventory").count() > 0:
            Group.objects.create(name="Mooring Inventory")
        if not MooringAreaGroup.objects.filter(name="Rottnest Island").count() > 0:
            MooringAreaGroup.objects.create(name="Rottnest Island")
        if not MooringAreaGroup.objects.filter(name="PVS").count() > 0:
            MooringAreaGroup.objects.create(name="PVS")