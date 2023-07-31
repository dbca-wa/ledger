from django.core.management.base import BaseCommand
from django.utils import timezone
from ledger.payments.bpoint.models import BpointTransaction, BpointToken
from ledger.payments.models import Invoice,OracleInterface,CashTransaction
from ledger.order.models import Order, Line as OrderLine
#from oscar.apps.order.models import Order
from ledger.basket.models import Basket
from django.conf import settings
from datetime import timedelta, datetime
from ledger.payments.bpoint.facade import Facade
from ledger.payments.bpoint.gateway import Gateway
from ledger.payments.models import OracleInterfaceSystem, OracleInterface, OracleParser, OracleParserInvoice 
from ledger.emails.emails import sendHtmlEmail
from ledger.payments import models as payment_models
from ledger.payments.models import TrackRefund, LinkedInvoice, OracleAccountCode, RefundFailed, OracleInterfaceSystem
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

           SYSTEM_ID = ''
           time_intervals = [
                   {"hour":"14", "day": -1,},
                   {"hour":"15", "day": -1,},
                   {"hour":"16", "day": -1,},
                   {"hour":"17", "day": -1,},
                   {"hour":"18", "day": -1,},
                   {"hour":"19", "day": -1,},
                   {"hour":"20", "day": -1,},
                   {"hour":"21", "day": -1,},
                   {"hour":"22", "day": -1,},
                   {"hour":"23", "day": -1,},
                   {"hour":"1", "day": 0,},
                   {"hour":"2", "day": 0,},
                   {"hour":"3", "day": 0,},
                   {"hour":"4", "day": 0,},
                   {"hour":"5", "day": 0,},
                   {"hour":"6", "day": 0,},
                   {"hour":"7", "day": 0,},
                   {"hour":"8", "day": 0,},
                   {"hour":"10", "day": 0,},
                   {"hour":"11", "day": 0,},
                   {"hour":"12", "day": 0,},
                   {"hour":"13", "day": 0,},
                   {"hour":"14", "day": 0,},
                   {"hour":"15", "day": 0,},
                   {"hour":"16", "day": 0,},
                   {"hour":"17", "day": 0,},
           ] 

           ois = None
           if options['system_id']:
                ois = payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api',enabled=True, system_id=options['system_id'])
           else:
                ois = payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api',enabled=True)
                
           for oracle_system in ois:
               print (oracle_system)
               linked_invoice_group_totals = {}
               rows = []
               used_bp_trans = []
               dupe_bp_trans = []
               no_bpoint_trans = []               
               SYSTEM_ID = oracle_system.system_id

               yesterday = datetime.today() - timedelta(days=1)
               settlement_date_search = yesterday.strftime("%Y%m%d")
               if options['settlement_date']:
                   settlement_date_search = options['settlement_date']
               settlement_date_search_obj = datetime.strptime(settlement_date_search, '%Y%m%d')

               for ti in time_intervals:
                    print (ti)
                    settlement_date_search_obj_delta = settlement_date_search_obj + timedelta(days=ti['day'])
                    start_li = settlement_date_search_obj_delta.strftime("%Y-%m-%d")+' '+ti['hour']+':00:00'
                    end_li = settlement_date_search_obj_delta.strftime("%Y-%m-%d")+' '+ti['hour']+':59:59'
                    print (start_li+" to "+end_li)

                    bpoint_total = D('0.00')
                    bpoint_transactions = []
                    bp_trans = BpointTransaction.objects.filter(settlement_date=settlement_date_search_obj, processed__gte=start_li, processed__lte=end_li,  crn1__startswith=SYSTEM_ID)
                    for bp in bp_trans:
                        if bp.action == 'payment':
                            bpoint_total = bpoint_total + bp.amount

                        if bp.action == 'refund':
                            bpoint_total = bpoint_total - bp.amount
                        bpoint_transactions.append(bp.crn1+' ('+str(bp.amount)+')')


                    order_total = D('0.00')
                    order_invoices = []
                    invoices = Invoice.objects.filter(settlement_date=settlement_date_search_obj, created__gte=start_li, created__lte=end_li, system=SYSTEM_ID)
                    for inv in invoices:
                        print (inv.order_number)
                        orders = Order.objects.filter(number=inv.order_number)
                        line_order_total = D('0.00')
                        for o in orders:
                            order_lines = OrderLine.objects.filter(order=o)
                            for ol in order_lines:

                                if 'order' in ol.payment_details:
                                   for pd_key,pd_val in ol.payment_details['order'].items():
                                       order_total = order_total + D(pd_val)
                                       line_order_total = line_order_total + D(pd_val)
                        order_invoices.append(inv.reference+' ('+str(line_order_total)+')')

                    row = {}
                    row['start_li'] = start_li
                    row['end_li'] = end_li
                    row['bpoint_total'] = bpoint_total
                    row['order_total'] = order_total
                    row['bpoint_transactions'] = bpoint_transactions
                    row['order_invoices'] = order_invoices
                    rows.append(row)
                    

               print (rows)

               if (len(rows)) > 0: # or (len(missing_records)) > 0 or (len(missing_records_in_ledger)) > 0:
                  print ("Sending Report")
                  context = {
                      'settlement_date' : settlement_date_search,
                      'rows' : rows,
                  }
                  print (context)
                  email_list = []
                  oirr = payment_models.OracleInterfaceReportReceipient.objects.filter(system=oracle_system)
                  for rr in oirr:
                         print (rr.email)
                         email_list.append(rr.email)
                  sendHtmlEmail(tuple(email_list),"[LEDGER] "+oracle_system.system_name+" Ledger Payment Time Based Audit Report for "+str(settlement_date_search)+" "+SYSTEM_ID,context,'email/bpoint_ledger_time_seperated_audit.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
                    
