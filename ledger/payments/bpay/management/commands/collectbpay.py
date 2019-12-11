from django.core.management.base import BaseCommand, CommandError
from ledger.payments.bpay.facade import bpayParser

class Command(BaseCommand):
    help = 'Reads the files in the commbank folder.'

    def add_arguments(self, parser):
        parser.add_argument('path')
    
    def handle(self, *args, **options):
        try:
            bpayParser(options['path'])
        except Exception as e:
            raise CommandError(e)
        
        self.stdout.write(self.style.SUCCESS('Parsed files successfully.'))
    
    