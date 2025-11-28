from __future__ import print_function

import csv
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, IntegrityError
from django.utils import timezone

from ledger.accounts.models import EmailUser

# Example CSV is
# first_name,last_name,email_address

class Command(BaseCommand):
    help = 'Create EmailUser records from a CSV file with headers: first_name,last_name,email_address'

    def add_arguments(self, parser):
        parser.add_argument('--csv', dest='csv_path', help='Path to CSV file', default=None)
        parser.add_argument('--dry-run', action='store_true', dest='dry_run', help='Run without creating users')

    def handle(self, *args, **options):
        csv_path = options.get('csv_path')
        dry_run = options.get('dry_run')

        if not csv_path:
            # Default to packaged CSV file
            csv_path = os.path.join(os.path.dirname(__file__), 'boranga-data-migration-users', 'boranga-data-migration-users.csv')

        if not os.path.exists(csv_path):
            raise CommandError('CSV file not found: {}'.format(csv_path))

        created = 0
        skipped = 0
        errors = 0

        with open(csv_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            required_fields = ['first_name', 'last_name', 'email_address']
            for f in required_fields:
                if f not in reader.fieldnames:
                    raise CommandError('CSV missing required header: {}'.format(f))

            for row_num, row in enumerate(reader, start=1):
                first = (row.get('first_name') or '').strip()
                last = (row.get('last_name') or '').strip()
                email = (row.get('email_address') or '').strip().lower()

                # Fail fast if first or last name missing
                if not first or not last:
                    raise CommandError('CSV row {} missing required first_name or last_name: {}'.format(row_num, row))

                if not email:
                    self.stderr.write('Skipping row with empty email: {} {}'.format(first, last))
                    skipped += 1
                    continue

                # Idempotent: skip if email already exists
                if EmailUser.objects.filter(email__iexact=email).exists():
                    self.stdout.write('Skipping existing user: {}'.format(email))
                    skipped += 1
                    continue

                if dry_run:
                    self.stdout.write('[dry-run] Would create: {} {} <{}>'.format(first, last, email))
                    created += 1
                    continue

                try:
                    with transaction.atomic():
                        user = EmailUser.objects.create(
                            email=email,
                            first_name=first,
                            last_name=last,
                            is_staff=False,
                            is_active=False,
                            date_joined=timezone.now()
                        )
                        # Set unusable password since these are migrated service accounts
                        user.set_unusable_password()
                        user.save()
                        created += 1
                        self.stdout.write('Created user: {}'.format(email))
                except IntegrityError as e:
                    self.stderr.write('IntegrityError creating {}: {}'.format(email, e))
                    errors += 1
                except Exception as e:
                    self.stderr.write('Error creating {}: {}'.format(email, e))
                    errors += 1

        self.stdout.write('\nSummary:')
        self.stdout.write('  Created: {}'.format(created))
        self.stdout.write('  Skipped: {}'.format(skipped))
        self.stdout.write('  Errors:  {}'.format(errors))