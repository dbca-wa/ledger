from django.core.management.base import BaseCommand, CommandError
from ledger.payments.bpay.facade import monthlyReport

class Command(BaseCommand):
    help = 'Generate a report with all unmatched transactions in bpay and sent to the relevant biller code recipients .'

    def handle(self, *args, **options):
        try:
            monthlyReport()
        except Exception as e:
            raise CommandError(e)
        
        self.stdout.write(self.style.SUCCESS('Generated BPAY monthly report.'))
    
    