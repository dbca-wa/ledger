from django.core.management.base import BaseCommand
from django.utils import timezone
from ledger.payments.bpoint.models import BpointTransaction, BpointToken
#from ledger.payments.models import Invoice,OracleInterface,CashTransaction
#from oscar.apps.order.models import Order
#from ledger.basket.models import Basket
from django.conf import settings
from datetime import timedelta, datetime
from ledger.payments.bpoint.facade import Facade
from ledger.emails.emails import sendHtmlEmail

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
           SYSTEM_ID = ''
           if settings.PS_PAYMENT_SYSTEM_ID:
                  SYSTEM_ID = settings.PS_PAYMENT_SYSTEM_ID.replace("S","0")
                  
           yesterday = datetime.today() - timedelta(days=1)
           settlement_date_search = yesterday.strftime("%Y%m%d")
           if options['settlement_date']:
               settlement_date_search = options['settlement_date']
           settlement_date_search_obj = datetime.strptime(settlement_date_search, '%Y%m%d')

           print ("Checking :"+settlement_date_search)
           bpoint_facade = Facade()
           b = bpoint_facade.fetch_transaction_by_settlement_date(settlement_date_search)
           ledger_payment_amount = 0
           bpoint_amount = 0
           recordcount = 0
           duplicate_check_array =[]
           for c in b:
                if c.bank_response_code == '00':
                    amount = str(c.amount)[:-2]+'.'+str(c.amount)[-2:]
                    if c.action == 'refund':
                        bpoint_amount = bpoint_amount - c.amount
                    else:
                        bpoint_amount = bpoint_amount + c.amount
                    
                    bpoint_amount_nice = str(bpoint_amount)[:-2]+'.'+str(bpoint_amount)[-2:]
                    bp_lpb_diff = bpoint_amount_nice
                    bp = BpointTransaction.objects.filter(crn1=c.crn1, action=c.action)
                    ledger_payment_settlement_date = ''
                    if bp.count() > 0:
                        ledger_payment_settlement_date = bp[0].settlement_date 
                        if bp[0].action == 'refund':
                            ledger_payment_amount = ledger_payment_amount - bp[0].amount
                        else:
                            ledger_payment_amount = ledger_payment_amount + bp[0].amount
                    bp_lpb_diff = float(bpoint_amount_nice) - float(ledger_payment_amount)
                    is_dupe = False
                    if c.crn1 in duplicate_check_array:
                        is_dupe = True
                    rows.append({'txn_number': c.txn_number,'crn1': c.crn1,'processed_date_time': c.processed_date_time, 'settlement_date': c.settlement_date, 'action': c.action, 'amount': amount, 'bpoint_amount': bpoint_amount_nice, 'ledger_payment_amount': ledger_payment_amount, 'bp_lpb_diff': bp_lpb_diff ,'ledger_payment_settlement_date': ledger_payment_settlement_date, 'is_dupe': is_dupe})
                    duplicate_check_array.append(c.crn1)
                    recordcount=recordcount + 1
           print ("Transaction count in Bpoint: "+str(recordcount))
           missing_records = []
           ledger_bpoint_count = 0
           bp1 = BpointTransaction.objects.filter(settlement_date=settlement_date_search_obj, crn1__istartswith=SYSTEM_ID)
           for rec in bp1:
                  exists = False
                  for c in b:
                      if rec.crn1 == c.crn1:
                          exists = True
                  if exists is False:
                         missing_records.append({'crn1': rec.crn1, 'created':rec.created, 'settlement_date': rec.settlement_date, 'amount': rec.amount,'action': rec.action})
                  ledger_bpoint_count = ledger_bpoint_count + 1
           print ("Ledger Bpoint Transaction count:" +str(ledger_bpoint_count))


           missing_records_in_ledger = []
           ledger_bpoint_count = 0
           bp1 = BpointTransaction.objects.filter(settlement_date=settlement_date_search_obj, crn1__istartswith=SYSTEM_ID)
           for c in b:
                  if c.bank_response_code == '00':
                     exists = False
                     for rec in bp1:
                         if rec.crn1 == c.crn1:
                             exists = True
                     if exists is False:
                            missing_records_in_ledger.append({'crn1': c.crn1, 'created':c.processed_date_time, 'settlement_date': c.settlement_date, 'amount':c.amount,'action': c.action})
                     ledger_bpoint_count = ledger_bpoint_count + 1
           print ("Ledger Bpoint Transaction count:" +str(ledger_bpoint_count))

           if  (len(rows)) > 0 or (len(missing_records)) > 0 or (len(missing_records_in_ledger)) > 0:
              print ("Sending Report")
              context = {
                  'settlement_date' : settlement_date_search,
                  'rows' : rows,
                  'missing_records': missing_records,
                  'missing_records_in_ledger' : missing_records_in_ledger
              }
              email_list = []
              for email_to in settings.NOTIFICATION_EMAIL.split(","):
                     email_list.append(email_to)
              sendHtmlEmail(tuple(email_list),"[LEDGER] Bpoint Ledger Payment Audit Report for "+str(settlement_date_search)+" "+SYSTEM_ID,context,'email/bpoint_ledger_payment_audit.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
                    