from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from ledger.accounts.models import EmailUser
from disturbance.components.compliances.models import Compliance, ComplianceUserAction
from disturbance.components.compliances.email import send_due_email_notification, send_internal_due_email_notification
import datetime

import itertools

class Command(BaseCommand):
    help = 'Change the status of Compliances from future to due when they are close to due date'

    def handle(self, *args, **options):
        today = timezone.now().date()
        timedelta = datetime.timedelta
        compare_date = timedelta(days=14) + today

        try:
            user = EmailUser.objects.get(email__icontains='cron')
        except:
            user = user = EmailUser.objects.create(email='cron@dbca.wa.gov.au', password = '')

        for c in Compliance.objects.filter(processing_status = 'future'):
            #if(c.due_date<= compare_date<= c.approval.expiry_date) and c.approval.status=='current':
            if(c.due_date<= compare_date) and (c.due_date<= c.approval.expiry_date) and c.approval.status=='current':
                try:
                    c.processing_status='due'
                    c.customer_status='due'
                    c.save()
                    send_due_email_notification(c)
                    send_internal_due_email_notification(c)
                    ComplianceUserAction.log_action(c,ComplianceUserAction.ACTION_STATUS_CHANGE.format(c.id),user)
                    print('Updated Compliance {} status to {}'.format(c.id,c.processing_status))
                except:
                    print('Error updating Compliance {} status'.format(c.id))