from django.core.management.base import BaseCommand
from django.utils import timezone
from ledger.payments.bpoint.models import BpointTransaction, BpointToken
from ledger.payments.bpoint.gateway import Gateway

#from ledger.payments.models import Invoice,OracleInterface,CashTransaction
#from oscar.apps.order.models import Order
#from ledger.basket.models import Basket
from django.conf import settings
from datetime import timedelta, datetime
from ledger.payments.bpoint.facade import Facade
from ledger.payments.models import OracleInterfaceSystem, OracleInterface, OracleParser, OracleParserInvoice 
from ledger.emails.emails import sendHtmlEmail
from ledger.payments import models as payment_models
import json
import os

class Command(BaseCommand):
    help = 'Check for payment which have been completed but are missing a booking.'

    def add_arguments(self, parser):
         yesterday = datetime.today() - timedelta(days=1)
         settlement_date_search = yesterday.strftime("%Y%m%d")
         parser.add_argument('settlement_date', nargs='?', default=settlement_date_search)
         parser.add_argument('system_id', nargs='?', default=None)

    def handle(self, *args, **options):
          
           SYSTEM_ID = ''

           ois = None
           if options['system_id']:
                ois = payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api',enabled=True, system_id=options['system_id'])
           else:
                ois = payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api',enabled=True)
                
           for oracle_system in ois:
               rows = []
               print (oracle_system)
               SYSTEM_ID = oracle_system.system_id 

               yesterday = datetime.today() - timedelta(days=1)
               settlement_date_search = yesterday.strftime("%Y%m%d")
               if options['settlement_date']:
                   settlement_date_search = options['settlement_date']
               settlement_date_search_obj = datetime.strptime(settlement_date_search, '%Y%m%d')

               print ("Checking :"+settlement_date_search)
               # Calculate Oracle Parse Data

               bpoint_facade = Facade()
               if oracle_system.integration_type == 'bpoint_api':
                    bpoint_facade.gateway = Gateway(
                        oracle_system.bpoint_username,
                        oracle_system.bpoint_password,
                        oracle_system.bpoint_merchant_num,
                        oracle_system.bpoint_currency,
                        oracle_system.bpoint_biller_code,
                        oracle_system.bpoint_test,
                        oracle_system.id
                    )
               
               b = bpoint_facade.fetch_transaction_by_settlement_date(settlement_date_search)
               ledger_payment_amount = 0
               bpoint_amount = 0
               bpoint_amount_nice = 0
               oracle_parser_amount = float('0.00')
               recordcount = 0
               duplicate_check_array =[]
               
               missing_records_in_ledger = []
               ledger_bpoint_count = 0
               bp1 = BpointTransaction.objects.filter(settlement_date=settlement_date_search_obj)
               for c in b:
                      if c.bank_response_code == '00' and c.response_code == '0':
                         exists = False
                         for rec in bp1:
                             if rec.txn_number == c.txn_number:
                                 exists = True
                         #exists = False
                         if c.action != 'reversal':
                            if exists is False:
                                    bpoint_amount_nice1 = str(c.amount)[:-2]+'.'+str(c.amount)[-2:]
                                    missing_records_in_ledger.append({'crn1': c.crn1, 'created':c.processed_date_time, 'settlement_date': c.settlement_date, 'amount':bpoint_amount_nice1,'action': c.action, 'txn_number': c.txn_number, 'card_details' : c.card_details.masked_card_number, 'rrn': c.rrn , 'original_txn_number' : c.original_txn_number , 'card_type' : c.card_type, 'receipt_number' : c.receipt_number, 'dvtoken': c.dvtoken })
                                    orignal_crn1 = ''
                                    if c.original_txn_number:
                                        bpoint_orginal = BpointTransaction.objects.filter(txn_number=c.original_txn_number)
                                        if bpoint_orginal.count() > 0:
                                            orignal_crn1 = bpoint_orginal[0].crn1
                                    BpointTransaction.objects.create(action=c.action,
                                                                    amount=bpoint_amount_nice1,
                                                                    amount_original=bpoint_amount_nice1,
                                                                    cardtype=c.card_type,
                                                                    crn1=c.crn1,
                                                                    original_crn1=orignal_crn1, 
                                                                    response_code=0, 
                                                                    response_txt='Approved', 
                                                                    receipt_number=c.receipt_number, 
                                                                    processed=c.processed_date_time, 
                                                                    settlement_date=datetime.strptime(c.settlement_date, "%Y%m%d").date(),
                                                                    type=c.type, 
                                                                    txn_number=c.txn_number,
                                                                    original_txn=c.original_txn_number,
                                                                    dvtoken=c.dvtoken,
                                                                    is_test=c.is_test_txn)

                            ledger_bpoint_count = ledger_bpoint_count + 1
               print ("Ledger Bpoint Transaction count:" +str(ledger_bpoint_count))

               # Totals

               if len(missing_records_in_ledger) > 0:
                  print ("Sending Report")
                  context = {
                      'settlement_date' : settlement_date_search,
                      'rows' : rows,
                      'missing_records_in_ledger' : missing_records_in_ledger,
                  }
                  email_list = []

                  oirr = payment_models.OracleInterfaceReportReceipient.objects.filter(system=oracle_system)
                  for rr in oirr:
                         print (rr.email)
                         email_list.append(rr.email)
                  sendHtmlEmail(tuple(email_list),"[LEDGER] "+oracle_system.system_name+" Bpoint Transactions Missing From Ledger "+str(settlement_date_search)+" "+SYSTEM_ID,context,'email/bpoint_ledger_payment_missing.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
                    
