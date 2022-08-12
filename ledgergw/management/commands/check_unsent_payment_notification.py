from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from ledger.payments import models as ledger_payment_models #OracleInterfaceSystem
from ledgergw import utils as ledgergw_utils
from decimal import *
from ledgergw.emails import sendHtmlEmail
import json
from datetime import timedelta, datetime
from ledger.basket import models as basket_models
import requests

class Command(BaseCommand):
    help = 'Resend URL Payment notification'

    def handle(self, *args, **options):
            today = datetime.today()# - timedelta(days=3)
            baskets = basket_models.Basket.objects.filter(notification_completed=False, notification_count__lte=5, status='Submitted')
            for b in baskets:
                if b.notification_url:
                   if len(b.notification_url) > 6:
                       try:
                           print ("Sending Ping to System")
                           print (b.id)
                           print (b.notification_url)
                           resp = requests.get(b.notification_url, verify=False)
                           #print (resp.status_code)
                           if resp.status_code == 200:
                              b.notification_completed = True
                              b.save()
                           else:
                              b.notification_count = b.notification_count + 1
                              b.notification_completed = False
                              b.save()

                       except:
                           b.notification_count = b.notification_count + 1
                           b.notification_completed = False 
                           b.save() 

                   else:
                       b.notification_completed=False
                       b.notification_count = b.notification_count + 1
                       b.save()
                else:
                    b.notification_completed=False
                    b.notification_count = b.notification_count + 1
                    b.save()

            


