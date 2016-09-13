from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Load all the fixtures'

    fixtures = [
        'conditions',
        'groups',
        'licences',
        'default-conditions',
        'returns',
        'regions',
        # 'catalogue',
        # 'partner'
    ]

    def handle(self, *args, **options):
        for fixture in self.fixtures:
            print('load {}'.format(fixture))
            call_command('loaddata', fixture)
