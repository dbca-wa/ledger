from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from disturbance.components.approvals.models import Approval
from ledger.accounts.models import EmailUser
from datetime import date, timedelta
from disturbance.components.approvals.email import (
    send_approval_renewal_email_notification,)



import itertools

class Command(BaseCommand):
    help = 'Send Approval renewal notice when approval is due expire in 30 days'

    def handle(self, *args, **options):
        try:
            user = EmailUser.objects.get(email__icontains='cron')
        except:
            user = user = EmailUser.objects.create(email='cron@dbca.wa.gov.au', password = '')

        expiry_notification_date = date.today() + timedelta(days=30)
        renewal_conditions = {
            'expiry_date__lte': expiry_notification_date,
            'renewal_sent': False,
            'replaced_by__isnull': True
        }

        for a in Approval.objects.filter(**renewal_conditions):
            if a.status == 'current' or a.status == 'suspended':
                try:
                    a.generate_renewal_doc()
                    send_approval_renewal_email_notification(a)
                    a.renewal_sent = True
                    a.save()
                    print('Renewal notice sent for Approval {}'.format(a.id))
                except:
                    print('Error sending renewal notice for Approval {}'.format(a.id))