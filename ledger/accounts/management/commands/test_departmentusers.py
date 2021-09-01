from django.core.management.base import BaseCommand, CommandError
from ledger.address.models import UserAddress
from ledger.accounts import common 

class Command(BaseCommand):
    help = 'Test Department Users.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print (common.retrieve_department_users())
        print (common.get_department_user('jason.moore@dbca.wa.gov.au'))
        print (common.get_department_user('jason.moore'))



