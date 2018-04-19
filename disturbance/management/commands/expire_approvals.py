from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from disturbance.components.approvals.models import Approval
from ledger.accounts.models import EmailUser
import datetime



import itertools

class Command(BaseCommand):
    help = 'Change the status of Approvals to Expired when past expiry date'

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email__icontains='cron')
        except:
            user = user = EmailUser.objects.create(email='cron@dbca.wa.gov.au', password = '')

        today = timezone.now().date()
        for a in Approval.objects.filter(status = 'current'):
            if a.expiry_date < today:
                try:
                    a.expire_approval(user)
                    a.save()
                    print('Updated Approval {} status to {}'.format(a.id,a.status))
                except:
                    print('Error updating Approval {} status'.format(a.id))

