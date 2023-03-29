from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from decimal import *
from ledgergw.emails import sendHtmlEmail
from decimal import Decimal
import json
from datetime import timedelta, datetime
from ledger.payments import utils as payments_utils
from ledger.payments.invoice import utils as invoice_utils
from ledger.accounts import models as accounts_models
from ledger.payments import models as payments_models
from ledger.payments.bpoint import models as bpoint_models
from ledger.payments.invoice import models as invoice_models
import os
import requests

class Command(BaseCommand):
    help = 'Bulk Refund Script for Ledger V2'

    def add_arguments(self, parser):
        parser.add_argument('file',)

    def handle(self, *args, **options):
        today = datetime.today()
        today_string = today.strftime("%Y-%m-%d-%H%M%S")
        file_path = options['file']
        
        #list_to_refund = ['PB-396291','PB-396289','PB-396277']
        list_to_refund = []
        with open(file_path) as file:
            list_to_refund = [line.rstrip() for line in file]
              
        
        report_rows = []
        refund_success = False
        refund_message = ''
        for booking_reference in list_to_refund:                        
                refund_success = False
                refund_message = ''
                invoice_lines = []
                system_id = None
                
                invoice_text = "Refund due to campsite closure"
                li = payments_models.LinkedInvoice.objects.filter(booking_reference=booking_reference)
                if li.count() > 0:
                    
                    lpic = payments_utils.ledger_payment_invoice_calulations(None, None, booking_reference, None, None)
                    print ("TOTAL START")
                    print (lpic['data']['total_gateway_amount'])
                    print (lpic['data']['total_oracle_amount'])
                    #print (lpic['data']['bp_txn_total'])
                    print ("TOTAL END")
                    booking_reference_linked = booking_reference                 
                    
                    if 'data' in lpic:
                        if lpic['data']['total_gateway_amount'] == lpic['data']['total_oracle_amount']:                 
                            
                            total_payment_gateway = lpic['data']['total_gateway_amount']
                            system_id = lpic['data']['linked_payments'][0]['system_identifier_system']
                            owner_id = lpic['data']['order'][0]['owner_id']
                            email_user = accounts_models.EmailUser.objects.get(id=owner_id)
                            #print (email_user.id)
                            #raise
                            for k,v in lpic['data']['oracle_code_totals'].items():
                                oracle_code = k
                                oracle_amount = v
                                print (str(k)+':'+str(v))
                                
                                invoice_lines.append({
                                    'ledger_description': 'Refund due to campsite closure',
                                    "quantity": 1,
                                    "price_incl_tax": str(Decimal(oracle_amount) - Decimal(oracle_amount) - Decimal(oracle_amount)),
                                    #"price_excl_tax": calculate_excl_gst(str(total_amount_child - total_amount_child- total_amount_child)),
                                    "oracle_code": oracle_code,
                                    "line_status" : 3 # status: 1= new , 2 = existing, 3 = removed
                                })

                            print (invoice_lines)

                            # Reversing Oracle Records
                            order = invoice_utils.create_submitted_basket_order_from_lines(booking_reference, invoice_lines, invoice_text, internal=False, order_total='0.00',user=email_user, booking_reference_linked=booking_reference_linked, system_id=system_id)
                            
                            # Preparing to Refund Payment
                            print ("BPOINT")
                            #info = {'amount': Decimal('{:.2f}'.format(float(refund_tx_pool[tx]))), 'details' : 'Refund via system'}
                            print (lpic['data']['bpoint'])
                            for b in lpic['data']['bpoint']:                                  
                                try:
                                    txn_total = lpic['data']['bp_txn_total'][b['txnnumber']]
                                    if txn_total > 0:                                    
                                        info = {'amount': Decimal('{:.2f}'.format(float(txn_total))), 'details' : 'Bulk Refund via system'}
                                        bpoint_trans = bpoint_models.BpointTransaction.objects.get(id=b['id'])
                                        #user = accounts_models.EmailUser.objects.get(id=1)
                                        raise
                                        refund = bpoint_trans.refund(info,email_user)                                                     
                                        invoice = invoice_models.Invoice.objects.get(reference=bpoint_trans.crn1)
                                        payments_utils.update_payments(invoice.reference)                                                                                
                                        print (bpoint_trans.id)
                                        refund_success = True
                                except Exception as e:
                                        refund_success = False
                                        refund_message = str(e)
                                        print ("EXCEPTION")
                                        print (e)
                                        failed_invoice_lines = []
                                        failed_invoice_lines.append({
                                            'ledger_description': 'Refund Failed moving funds to unallocated',
                                            "quantity": 1,
                                            "price_incl_tax": str(txn_total),
                                            #"price_excl_tax": calculate_excl_gst(str(total_amount_child - total_amount_child- total_amount_child)),
                                            "oracle_code": settings.UNALLOCATED_ORACLE_CODE,
                                            "line_status" : 3 # status: 1= new , 2 = existing, 3 = removed
                                        })
                                        failed_order = invoice_utils.create_submitted_basket_order_from_lines(booking_reference, failed_invoice_lines, invoice_text, internal=False, order_total='0.00',user=email_user, booking_reference_linked=booking_reference_linked, system_id=system_id)

                                        # create failed refund record                                                                                                                          
                                        payments_models.RefundFailed.objects.create(invoice_group=li[0].invoice_group_id,
                                                                         booking_reference=booking_reference,
                                                                         invoice_reference=li[0].invoice_reference,
                                                                         refund_amount=Decimal(txn_total),
                                                                         status=0,
                                                                         basket_json="{}",
                                                                         system_identifier=li[0].system_identifier,
                                                                        )

                                        #print (b)
                            # TODO 

                            # 1. Perform refund (support for mulitple bpoint transaction) - DONE
                            
                            # 2. Create record for BPOINT transactions that fail to refund. -DONE

                            # 3. Create FAILD refunds - DONE 

                            # 4. Email report of refunds - DONE 
                        else:
                             refund_message = "oracle and bpoint totals do not match"

                else:
                    refund_message = "booking reference not found"
                    refund_success = False
                    print ("booking reference not found : "+str(booking_reference))                

                report_rows.append({'booking_reference' : booking_reference, 'refund_success': refund_success, 'message': refund_message})
                #report_csv = ','.join(map(str, report_rows)) 

        print (report_rows)
        f = open(os.path.join(settings.BASE_DIR, 'logs', 'ledger_bulkrefunds_'+today_string+'.log'), "a")
        for r in report_rows:
            print (r['booking_reference'])
            f.write(r['booking_reference']+","+str(r['refund_success'])+","+r['message']+"\n")                
        f.close()


        


            


