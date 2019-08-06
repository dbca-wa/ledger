from django.core.management.base import BaseCommand, CommandError
from oscar.apps.payment.exceptions import UnableToTakePayment
from ledger.payments.bpoint.models import UsedBpointToken
from ledger.payments.facade import bpoint_facade

class Command(BaseCommand):
    help = 'Delete unused tokens from bpoint.'

    def handle(self, *args, **options):
        tokens = UsedBpointToken.objects.all()
        try:
            for t in tokens:
                bpoint_facade.delete_token(t.DVToken)
                t.delete()
        except UnableToTakePayment:
            pass
        except Exception as e:
            raise CommandError(e)

        self.stdout.write(self.style.SUCCESS('Processed unused tokens.'))