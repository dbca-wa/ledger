from django.core.management.base import BaseCommand
from django.utils import timezone
from ledger.payments.bpoint.models import BpointTransaction, BpointToken
from ledger.payments.models import Invoice,OracleInterface,CashTransaction
from ledger.order.models import Order, Line as OrderLine
#from oscar.apps.order.models import Order
#from ledger.basket.models import Basket
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
               print (oracle_system)
               linked_invoice_group_totals = {}
               rows = []               
               SYSTEM_ID = oracle_system.system_id 

               yesterday = datetime.today() - timedelta(days=1)
               settlement_date_search = yesterday.strftime("%Y%m%d")
               if options['settlement_date']:
                   settlement_date_search = options['settlement_date']
               settlement_date_search_obj = datetime.strptime(settlement_date_search, '%Y%m%d')
               start_li = settlement_date_search_obj.strftime("%Y-%m-%d")+' 00:00'
               end_li = settlement_date_search_obj.strftime("%Y-%m-%d")+' 23:59'
               print (start_li+" to "+end_li)
               linked_invoices = LinkedInvoice.objects.filter(created__gte=start_li,created__lte=end_li, system_identifier=oracle_system).values('invoice_group_id').distinct()

               #linked_invoices = LinkedInvoice.objects.filter(invoice_group_id=68682).values('invoice_group_id').distinct()
               for li in linked_invoices:
                   #print (li.invoice_reference)
                   linked_invoice_groups = LinkedInvoice.objects.filter(invoice_group_id=li['invoice_group_id'])
                   linked_invoice_group_totals[li['invoice_group_id']] = {"bpoint_total" : D('0.00'), "oracle_order_total": D('0.00'), "invoices": []}
                   for lig in linked_invoice_groups:
                       if lig.invoice_reference not in linked_invoice_group_totals[li['invoice_group_id']]["invoices"]:
                           bpoint_trans = BpointTransaction.objects.filter(crn1=lig.invoice_reference)
                           for bt in bpoint_trans:
                                if bt.action == 'payment':
                                    linked_invoice_group_totals[li['invoice_group_id']]["bpoint_total"] = linked_invoice_group_totals[li['invoice_group_id']]["bpoint_total"] + bt.amount
                                if bt.action == 'refund':
                                    linked_invoice_group_totals[li['invoice_group_id']]["bpoint_total"] = linked_invoice_group_totals[li['invoice_group_id']]["bpoint_total"] - bt.amount
                           linked_invoice_group_totals[li['invoice_group_id']]["invoices"].append(lig.invoice_reference)

                           invoices = Invoice.objects.filter(reference=lig.invoice_reference)
                           for inv in invoices:
                                orders = Order.objects.filter(number=inv.order_number)
                                for o in orders:
                                    order_lines = OrderLine.objects.filter(order=o)
                                    for ol in order_lines:
                                        if 'order' in ol.payment_details:
                                           for pd_key,pd_val in ol.payment_details['order'].items():
                                               linked_invoice_group_totals[li['invoice_group_id']]["oracle_order_total"] = linked_invoice_group_totals[li['invoice_group_id']]["oracle_order_total"] + D(pd_val)

               rows = []
               for ligt in linked_invoice_group_totals:
                   if linked_invoice_group_totals[ligt]["bpoint_total"] == linked_invoice_group_totals[ligt]["oracle_order_total"]:
                       pass
                   else:
                       row = {"invoice_group_id" : ligt, "bpoint_total": linked_invoice_group_totals[ligt]["bpoint_total"], "oracle_order_total": linked_invoice_group_totals[ligt]["oracle_order_total"], "invoices": linked_invoice_group_totals[ligt]["invoices"]}
                       rows.append(row)

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
                    
