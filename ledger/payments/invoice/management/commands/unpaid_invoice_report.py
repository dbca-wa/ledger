from django.core.management.base import BaseCommand
from django.utils import timezone
from ledger.payments.models import Invoice
# from ledger.order.models import Order, Line as OrderLine
#from oscar.apps.order.models import Order
# from ledger.basket.models import Basket
from django.conf import settings
from datetime import timedelta, datetime
# from ledger.payments.bpoint.facade import Facade
# from ledger.payments.bpoint.gateway import Gateway
from ledger.payments.models import OracleInterfaceSystem, OracleInterface, OracleParser, OracleParserInvoice 
from ledger.emails.emails import sendHtmlEmail
from ledger.payments import models as payment_models
from ledger.emails import email_templates
# from ledger.payments.models import TrackRefund, LinkedInvoice, OracleAccountCode, RefundFailed, OracleInterfaceSystem
# from decimal import Decimal as D
from hashlib import md5
import xlsxwriter
import json
import os

class Command(BaseCommand):
    help = 'Will produce a report of unpaid invoices to be used as a debtor report.'

    def add_arguments(self, parser):        
        #  yesterday = datetime.today() - timedelta(days=1)
        #  settlement_date_search = yesterday.strftime("%Y%m%d")
        #  parser.add_argument('settlement_date', nargs='?', default=settlement_date_search)
        parser.add_argument('system_id', nargs='?', default=None)

    def handle(self, *args, **options):

            SYSTEM_ID = ''
            ois = None
            print (options['system_id'])
            if options['system_id']:
                ois = payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api',enabled=True, system_id=options['system_id'])
            else:
                # print ("No system id provided")
                # return
                ois = payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api',enabled=True)
                        
            plaintext = str(datetime.now()) # Must be a string, doesn't need to have utf-8 encoding
            md5hash = md5(plaintext.encode('utf-8')).hexdigest()
            if os.path.isdir(str(settings.BASE_DIR)+'/tmp/') is False:
                os.makedirs(str(settings.BASE_DIR)+'/tmp/')
            excel_file = str(settings.BASE_DIR)+'/tmp/'+md5hash+'.xlsx'
            print (excel_file)
            workbook = xlsxwriter.Workbook(excel_file)                        
            worksheet = workbook.add_worksheet("Unpaid Invoice Report")
            format = workbook.add_format()
            format.set_pattern(1)
            format.set_bg_color('black')
            format.set_font_color('white') 
            format.set_bold()
            col = 0 
            row = 0
            worksheet.write(row, col, "CREATED", format)
            worksheet.set_column(0, 0, 12)
            worksheet.write(row, col + 1, "INVOICE NO",format)
            worksheet.set_column(1, 1, 30)
            worksheet.write(row, col + 2, "AMOUNT",format)
            worksheet.set_column(2, 2, 30)
            worksheet.write(row, col + 3, "PAYMENT STATUS",format)
            worksheet.set_column(3, 3, 20)
            worksheet.write(row, col + 4, "DUE DATE",format)
            worksheet.set_column(4, 4, 20)       
            worksheet.write(row, col + 5, "DUE STATUS",format)
            worksheet.set_column(5, 5, 20)               
            row += 1

            for oracle_system in ois:
                print (oracle_system)
                SYSTEM_ID = oracle_system.system_id
                print (SYSTEM_ID)
                iv = Invoice.objects.filter(reference__startswith=SYSTEM_ID)                
                    
                for i in iv:
                    print ("Looking at invoice: "+i.reference)
    
                    payment_status = i.payment_status
                     
                    if payment_status == 'paid' or payment_status == 'over_paid' or payment_status == 'cancelled':  
                         pass
                    else:      
                        worksheet.write(row, col, i.created.astimezone().strftime('%d/%m/%Y'))
                        worksheet.write(row, col + 1, i.reference)
                        worksheet.write(row, col + 2, i.amount)
                        worksheet.write(row, col + 3, payment_status)
                        due_date = ""
                        if i.due_date is not None:
                            due_date = i.due_date.strftime('%d/%m/%Y')
                        worksheet.write(row, col + 4, due_date)
                        due_status  = "Not Due"
                        if payment_status == 'paid' or payment_status == 'over_paid':                        
                            due_status  = "Paid"
                        else:
                            if i.due_date:
                                if datetime.now().date() > i.due_date:
                                    due_status  = "Overdue"
                                else:
                                    due_status  = "Not Due"
                            else:
                                due_status = "Unknown"
                        worksheet.write(row, col + 5, due_status)
                        row += 1

                workbook.close()     
                file_buffer = None
                with open(excel_file, 'rb') as f:
                    file_buffer = f.read()                    

                dt = datetime.now().astimezone().strftime('%Y-%m-%d-%H%M')
                t = email_templates.DebtorReport()
                t.subject = "Debtor Report (Unpaid Invoices)"
                to_addresses=[]
                oirr = payment_models.OracleInterfaceReportReceipient.objects.filter(system=oracle_system)
                for rr in oirr:
                        print (rr.email)
                        to_addresses.append(rr.email)
                t.send(to_addresses=to_addresses, context={"settings": settings,'body': 'Please see attached a unpaid invoice report.'}, headers={"Reply-To": settings.EMAIL_FROM},attachments=[('Debtor Report {}.xlsx'.format(dt), file_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')])        
            