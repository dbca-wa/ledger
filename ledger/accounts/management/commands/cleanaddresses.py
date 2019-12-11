from django.core.management.base import BaseCommand, CommandError
from ledger.address.models import UserAddress

class Command(BaseCommand):
    help = 'Cleans up the oscar user address table.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        try:
            addresses = UserAddress.objects.all()
            for a in addresses:
                if not a.profile_addresses.all():
                    a.delete()
        except Exception as e:
            raise CommandError(e)

        self.stdout.write(self.style.SUCCESS('Cleaned up oscar addresses.'))