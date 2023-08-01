from django.core.management.base import BaseCommand
from django.utils import timezone
from ledger.payments.bpoint.models import BpointTransaction, BpointToken
#from ledger.payments.models import Invoice,OracleInterface,CashTransaction
#from oscar.apps.order.models import Order
#from ledger.basket.models import Basket
from django.conf import settings
from datetime import timedelta, datetime
from ledger.payments.bpoint.facade import Facade
from ledger.payments.bpoint.gateway import Gateway
from ledger.payments.models import OracleInterfaceSystem, OracleInterface, OracleParser, OracleParserInvoice, PaymentTotal
from ledger.emails.emails import sendHtmlEmail
from ledger.payments import models as payment_models
from decimal import Decimal as D
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
           
           #system = settings.PS_PAYMENT_SYSTEM_ID
           #system = system.replace('S','0')
           #rows = bpoint_integrity_checks(system,100,2)
           SYSTEM_ID = ''
           #if settings.PS_PAYMENT_SYSTEM_ID:
           #       SYSTEM_ID = settings.PS_PAYMENT_SYSTEM_ID.replace("S","0")
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
               parser_invoice_totals = {}
               op = OracleParser.objects.filter(date_parsed=settlement_date_search_obj)
               if op.count() > 0:
                    opi = OracleParserInvoice.objects.filter(parser=op).order_by('reference')

                    for entry in opi:
                        if entry.reference[:4] == SYSTEM_ID:
                            parser_invoice_totals[entry.reference] = float('0.00')
                            entrydetails = json.loads(entry.details)
                            parser_amount = float('0.00')
                            for t in entrydetails:
                               if 'order' in entrydetails[t]:
                                  parser_amount = float(entrydetails[t]['order'])
                                  parser_invoice_totals[entry.reference] = parser_invoice_totals[entry.reference] +  parser_amount

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
               for c in b:
                    if c.bank_response_code == '00' and c.response_code == '0':
                        amount = str(c.amount)[:-2]+'.'+str(c.amount)[-2:]
                        # Skip reversal as these do not impact bpoint settlement totals
                        if c.action == 'reversal':
                            continue

                        if c.action == 'refund':
                            bpoint_amount = bpoint_amount - c.amount
                        elif c.action == 'reversal':
                             pass
                        #    bpoint_amount = bpoint_amount - c.amount
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
                            elif bp[0].action == 'reversal':
                                pass
                            else:
                                ledger_payment_amount = ledger_payment_amount + bp[0].amount
                        bp_lpb_diff = float(bpoint_amount_nice) - float(ledger_payment_amount)
                        is_dupe = False
                        if c.crn1 in duplicate_check_array:
                            is_dupe = True

                        if c.crn1 in parser_invoice_totals:
                            oracle_parser_amount = float(oracle_parser_amount) + float(parser_invoice_totals[c.crn1])

                        rows.append({'txn_number': c.txn_number,'crn1': c.crn1,'processed_date_time': c.processed_date_time, 'settlement_date': c.settlement_date, 'action': c.action, 'amount': amount, 'bpoint_amount': bpoint_amount_nice, 'ledger_payment_amount': ledger_payment_amount, 'bp_lpb_diff': bp_lpb_diff ,'ledger_payment_settlement_date': ledger_payment_settlement_date, 'is_dupe': is_dupe, 'oracle_parser_amount': oracle_parser_amount})
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
               bp1 = BpointTransaction.objects.filter(settlement_date=settlement_date_search_obj, crn1__istartswith=SYSTEM_ID).order_by('processed')
               for c in b:
                      if c.bank_response_code == '00' and c.response_code == '0':
                         exists = False
                         for rec in bp1:
                             if rec.crn1 == c.crn1:
                                 exists = True
                         if exists is False:
                                bpoint_amount_nice1 = str(c.amount)[:-2]+'.'+str(c.amount)[-2:]
                                missing_records_in_ledger.append({'crn1': c.crn1, 'created':c.processed_date_time, 'settlement_date': c.settlement_date, 'amount':bpoint_amount_nice1,'action': c.action})
                         ledger_bpoint_count = ledger_bpoint_count + 1
               print ("Ledger Bpoint Transaction count:" +str(ledger_bpoint_count))

               # Totals
               ledger_payment_amount_total = 0
               ledger_payment_amount_total_rolling_totals = []
               bp_ledger_payment_refund = BpointTransaction.objects.filter(settlement_date=settlement_date_search_obj, crn1__istartswith=SYSTEM_ID)
               for bpl in bp_ledger_payment_refund:
                    if bpl.action == 'refund':
                        ledger_payment_amount_total = ledger_payment_amount_total - bpl.amount
                    else:
                        ledger_payment_amount_total = ledger_payment_amount_total + bpl.amount
                    ledger_payment_amount_total_rolling_totals.append({'invoice': bpl.crn1, 'amount': bpl.amount, 'rolling_total': ledger_payment_amount_total })



               ofs = OracleInterfaceSystem.objects.filter(system_id=SYSTEM_ID)
               source = ''
               oracle_receipts_total = 0
               if ofs.count() > 0:
                   source = ofs[0].source
                   oi_receipts = OracleInterface.objects.filter(source=source, receipt_date=settlement_date_search_obj)
                   for oir in oi_receipts:
                        oracle_receipts_total = oracle_receipts_total + oir.amount
               
               parser_invoice_totals_rolling_totals = []
               parser_rolling_total = float('0.00')
               for pi in parser_invoice_totals:    
                   parser_rolling_total = parser_rolling_total + parser_invoice_totals[pi]
                   parser_invoice_totals_rolling_totals.append({'invoice': pi, 'amount': parser_invoice_totals[pi], 'rolling_total': parser_rolling_total })
               parser_total = parser_rolling_total

               pt = PaymentTotal.objects.filter(oracle_system=oracle_system,settlement_date=settlement_date_search_obj)
               if pt.count() > 0:
                   pt_obj = PaymentTotal.objects.get(id=pt[0].id)
                   pt_obj.oracle_system=oracle_system
                   pt_obj.settlement_date=settlement_date_search_obj
                   pt_obj.bpoint_gateway_total=D(bpoint_amount_nice)
                   pt_obj.ledger_bpoint_total=D(ledger_payment_amount_total)
                   pt_obj.oracle_parser_total=D(parser_total)
                   pt_obj.oracle_receipt_total=D(oracle_receipts_total)
                   pt_obj.updated = datetime.now()
                   pt_obj.save()

               
               else:                    
                    PaymentTotal.objects.create( oracle_system=oracle_system,
                                                 settlement_date=settlement_date_search_obj,
                                                 bpoint_gateway_total=D(bpoint_amount_nice),
                                                 ledger_bpoint_total=D(ledger_payment_amount_total),
                                                 oracle_parser_total=D(parser_total),
                                                 oracle_receipt_total=D(oracle_receipts_total),
                                                 cash_total='0.00',
                                                 bpay_total='0.00',
                                               )


               if  (len(rows)) > 0 or (len(missing_records)) > 0 or (len(missing_records_in_ledger)) > 0:
                  print ("Sending Report")
                  context = {
                      'settlement_date' : settlement_date_search,
                      'rows' : rows,
                      'missing_records': missing_records,
                      'missing_records_in_ledger' : missing_records_in_ledger,
                      'bpoint_total_amount': bpoint_amount_nice,
                      'ledger_payment_amount_total' : ledger_payment_amount_total,
                      'ledger_payment_amount_total_rolling_totals' :  ledger_payment_amount_total_rolling_totals,
                      'oracle_receipts_total' : oracle_receipts_total,
                      'parser_total': parser_total,
                      'parser_invoice_totals' : parser_invoice_totals,
                      'parser_invoice_totals_rolling_totals' : parser_invoice_totals_rolling_totals
                  }
                  email_list = []

                  oirr = payment_models.OracleInterfaceReportReceipient.objects.filter(system=oracle_system)
                  for rr in oirr:
                         print (rr.email)
                         email_list.append(rr.email)
                  sendHtmlEmail(tuple(email_list),"[LEDGER] "+oracle_system.system_name+" Ledger Payment Audit Report for "+str(settlement_date_search)+" "+SYSTEM_ID,context,'email/bpoint_ledger_payment_audit.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
                    
