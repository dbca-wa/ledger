from django.core.management.base import BaseCommand
from ledger.taxonomy.models import Species


class Command(BaseCommand):
    help = 'Updates local species names from remote sources'

    def handle(self, *args, **kwargs):
        Species.objects.update_herbie_hbvspecies()
