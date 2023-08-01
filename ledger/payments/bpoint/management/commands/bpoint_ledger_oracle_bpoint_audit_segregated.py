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

           ois = None
           if options['system_id']:
                ois = payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api',enabled=True, system_id=options['system_id'])
           else:
                ois = payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api',enabled=True)
                
           for oracle_system in ois:
               linked_invoice_group_totals = {}
               rows = []
               used_bp_trans = []
               dupe_bp_trans = []
               no_bpoint_trans = []
               print (oracle_system)
               
               SYSTEM_ID = oracle_system.system_id

               yesterday = datetime.today() - timedelta(days=1)
               settlement_date_search = yesterday.strftime("%Y%m%d")
               if options['settlement_date']:
                   settlement_date_search = options['settlement_date']

               settlement_date_search_obj = datetime.strptime(settlement_date_search, '%Y%m%d')
               start_li = settlement_date_search_obj.strftime("%Y-%m-%d")+' 00:00'
               end_li = settlement_date_search_obj.strftime("%Y-%m-%d")+' 23:59'
               print (start_li+" to "+end_li)

               invoices = Invoice.objects.filter(settlement_date=settlement_date_search_obj)
               for inv in invoices:
                   #print (inv.order_number)
                   bpoint_trans = True
                   bp_trans = BpointTransaction.objects.filter(crn1=inv.reference, settlement_date=settlement_date_search_obj)
                   if bp_trans.count() > 0:
                       for bp in bp_trans:
                           if bp.receipt_number in used_bp_trans:
                              dupe_bp_trans.append(bp.receipt_number)
                           else:
                              used_bp_trans.append(bp.receipt_number)
                   else:
                       if inv.amount > 0:
                           #no_bpoint_trans.append(inv.reference)
                           bpoint_trans = False

                           #print (bp.amount)

                   order_total = D('0.00')
                   orders = Order.objects.filter(number=inv.order_number)
                   for o in orders:
                       order_lines = OrderLine.objects.filter(order=o)
                       for ol in order_lines:
                           if 'order' in ol.payment_details:
                              for pd_key,pd_val in ol.payment_details['order'].items():
                                  order_total = order_total + D(pd_val)
                
                                  #print (pd_val)
                   if order_total > 0 and bpoint_trans is False:
                          no_bpoint_trans.append(inv.reference)
               print (settlement_date_search_obj)
               print (dupe_bp_trans)
               print (no_bpoint_trans)

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
                  sendHtmlEmail(tuple(email_list),"[LEDGER] "+oracle_system.system_name+" Ledger Payment Oracle Order Discrepancy Report for "+str(settlement_date_search)+" "+SYSTEM_ID,context,'email/bpoint_ledger_oracle_audit.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
                    
