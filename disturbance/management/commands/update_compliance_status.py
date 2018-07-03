from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from disturbance.components.compliances.models import Compliance
import datetime



import itertools

class Command(BaseCommand):
    help = 'Change the status of Compliances from future to due when they are close to due date'

    def handle(self, *args, **options):
        today = timezone.now().date()
        timedelta = datetime.timedelta
        compare_date = timedelta(days=14) + today

        for c in Compliance.objects.filter(processing_status = 'future'):
            #if(c.due_date<= compare_date<= c.approval.expiry_date) and c.approval.status=='current':
            if(c.due_date<= compare_date) and (c.due_date<= c.approval.expiry_date) and c.approval.status=='current':
                try:
                    c.processing_status='due'
                    c.customer_status='due'
                    c.save()
                    print('updated Compliance {} status to {}'.format(c.id,c.processing_status))
                except:
                    print('Error updating Compliance {} status'.format(c.id))