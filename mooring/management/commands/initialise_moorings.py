from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core import management
from mooring.management.commands import set_global_settings, set_groups
import json

from datetime import timedelta

class Command(BaseCommand):
    help = 'Set auth groups.'

    def handle(self, *args, **options):
        management.call_command('set_global_settings')
        management.call_command('set_groups')