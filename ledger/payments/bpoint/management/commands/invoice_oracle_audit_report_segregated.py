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
from ledger.payments.models import TrackRefund, LinkedInvoice, OracleAccountCode, RefundFailed, OracleInterfaceSystem, OracleParserInvoice

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
            invoice_store_obj = {}
            print (options)
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
                
                audit_totals = {}
                oracle_invoices = OracleParserInvoice.objects.filter(parser__date_parsed=settlement_date_search_obj,reference__startswith=oracle_system.system_id)
                # print (oracle_invoices)
                for oi in oracle_invoices:
                    oracle_invoice_total = 0
                    # print (oi.reference)
                    #print (oi.details)
                    if oi.reference in invoice_store_obj:
                         pass
                    else:
                        audit_totals[oi.reference] = {"oracle_total": 0, "invoice_total": 0, "bpoint_total": 0}
                    details_json = json.loads(oi.details)

                    for id_key in details_json.keys():
                        #print (id_key)
                        #print (details_json[id_key]['order'])
                        oracle_invoice_total = oracle_invoice_total + float(details_json[id_key]['order'])
                        #for oracle_code_key in details_json[id_key].keys():
                        #    print (oracle_code_key)
                        #print ("INV")
                        
                        #print (invoice_obj.amount)
                        #print (oracle_invoice_total)
                    invoice_obj = Invoice.objects.get(reference=oi.reference)
                    bpoint_payment = BpointTransaction.objects.filter(crn1=oi.reference)
                    if bpoint_payment.count() > 0:
                        if bpoint_payment[0].action == 'refund':
                            bpoint_payment_total = bpoint_payment[0].amount - bpoint_payment[0].amount - bpoint_payment[0].amount
                        else:
                            bpoint_payment_total = bpoint_payment[0].amount
                    else:
                        bpoint_payment_total = D("0.00")
                    oracle_invoice_in_decimal = D("{:.2f}".format(oracle_invoice_total))
                    audit_totals[oi.reference]["oracle_total"] = oracle_invoice_in_decimal
                    audit_totals[oi.reference]["invoice_total"] = invoice_obj.amount
                    audit_totals[oi.reference]["bpoint_total"] = bpoint_payment_total
                    

                    if oracle_invoice_in_decimal != invoice_obj.amount:
                        print ("Descrpency")
                        print (oi.reference)
                        print (audit_totals[oi.reference])
                    if oracle_invoice_in_decimal != bpoint_payment_total:
                        print ("Descrpency")
                        print (oi.reference)
                        print (audit_totals[oi.reference])                 

                    if invoice_obj.amount != bpoint_payment_total:
                        print ("Descrpency")
                        print (oi.reference)
                        print (audit_totals[oi.reference])                                     


                # invoices = Invoice.objects.filter(settlement_date=settlement_date_search_obj,reference__startswith=oracle_system.system_id)
                # for inv in invoices:
                #     if inv.reference not in invoice_store_obj:
                #         bpoint_payment_exists = BpointTransaction.objects.filter(crn1=inv.reference).exists()
                #         print ("Not in store obj : {} {} {}".format(inv.reference, inv.amount, bpoint_payment_exists))
                         

                # print (audit_totals)

                # rows = []
                # for ligt in linked_invoice_group_totals:
                #     if linked_invoice_group_totals[ligt]["bpoint_total"] == linked_invoice_group_totals[ligt]["oracle_order_total"]:
                #         pass
                #     else:
                #         row = {"invoice_group_id" : ligt, "bpoint_total": linked_invoice_group_totals[ligt]["bpoint_total"], "oracle_order_total": linked_invoice_group_totals[ligt]["oracle_order_total"], "invoices": linked_invoice_group_totals[ligt]["invoices"]}
                #         rows.append(row)

                # if (len(rows)) > 0: # or (len(missing_records)) > 0 or (len(missing_records_in_ledger)) > 0:
                #     print ("Sending Report")
                #     context = {
                #         'settlement_date' : settlement_date_search,
                #         'rows' : rows,
                #     }
                #     print (context)
                #     email_list = []
                #     oirr = payment_models.OracleInterfaceReportReceipient.objects.filter(system=oracle_system)
                #     for rr in oirr:
                #             print (rr.email)
                #             email_list.append(rr.email)
                #     sendHtmlEmail(tuple(email_list),"[LEDGER] "+oracle_system.system_name+" Ledger Payment Oracle Order Discrepancy Report for "+str(settlement_date_search)+" "+SYSTEM_ID,context,'email/bpoint_ledger_oracle_audit.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
                        
