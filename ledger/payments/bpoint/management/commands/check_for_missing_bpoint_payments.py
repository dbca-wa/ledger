from django.core.management.base import BaseCommand
from django.utils import timezone
from mooring import models 
from ledger.payments.bpoint.models import BpointTransaction, BpointToken
#from ledger.payments.models import Invoice,OracleInterface,CashTransaction
#from oscar.apps.order.models import Order
#from ledger.basket.models import Basket
from django.conf import settings
from datetime import timedelta, datetime
from ledger.payments.bpoint.facade import Facade
from mooring.emails import sendHtmlEmail

class Command(BaseCommand):
    help = 'Check for payment which have been completed but are missing a booking.'

    def add_arguments(self, parser):
         yesterday = datetime.today() - timedelta(days=1)
         settlement_date_search = yesterday.strftime("%Y%m%d")
         parser.add_argument('settlement_date', nargs='?', default=settlement_date_search)

    def handle(self, *args, **options):
           rows = []
           #system = settings.PS_PAYMENT_SYSTEM_ID
           #system = system.replace('S','0')
           #rows = bpoint_integrity_checks(system,100,2)
           yesterday = datetime.today() - timedelta(days=1)
           settlement_date_search = yesterday.strftime("%Y%m%d")
           if options['settlement_date']:
               settlement_date_search = options['settlement_date']
           print ("Checking :"+settlement_date_search)
           bpoint_facade = Facade()
           b = bpoint_facade.fetch_transaction_by_settlement_date(settlement_date_search)
           for c in b:
                bp = BpointTransaction.objects.filter(crn1=c.crn1)
                if bp.count() > 0:
                    pass
                else:
                    pass
                    rows.append({'txn_number': c.txn_number,'crn1': c.crn1,'processed_date_time': c.processed_date_time, 'settlement_date': c.settlement_date })

           #print ("Error: Sending Email Notification: "+settings.NOTIFICATION_EMAIL)
           if  (len(rows)) > 0:
              print ("Sending Report")
              context = {
                  'settlement_date' : settlement_date_search,
                  'rows' : rows
              }
              email_list = []
              for email_to in settings.NOTIFICATION_EMAIL.split(","):
                     email_list.append(email_to)
              sendHtmlEmail(tuple(email_list),"[LEDGER] Missing Bpoint Payments",context,'email/missing_payments.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
                    
