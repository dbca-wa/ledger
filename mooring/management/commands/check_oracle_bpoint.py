from django.core.management.base import BaseCommand
from django.utils import timezone
from mooring.models import GlobalSettings, MooringAreaGroup
from ledger.payments.bpoint.models import BpointTransaction, BpointToken
from ledger.payments.models import Invoice,OracleInterface,CashTransaction
from oscar.apps.order.models import Order
from django.core.exceptions import ValidationError
from django.conf import settings
from decimal import *
from mooring.emails import sendHtmlEmail
import json

from datetime import timedelta, datetime

class Command(BaseCommand):
    help = 'Check BPOINT Settlement dates with oracle Invoice Settlement dates to ensure totals match.'

    def handle(self, *args, **options):
            bpoint_total = Decimal('0.00')
            oracle_total = Decimal('0.00')
            invoice_total = Decimal('0.00')
            today = datetime.today()# - timedelta(days=3)
            system = settings.PS_PAYMENT_SYSTEM_ID
            system = system.replace('S','0')
            print (system)
            try:
                 print ("Calculation Bpoint Transaction Total")
                 bpoint_trans = BpointTransaction.objects.filter(settlement_date=today, crn1__istartswith=system)
                 for i in bpoint_trans:
                      if i.action == 'payment':
                              bpoint_total = bpoint_total + Decimal(i.amount)
                      if i.action == 'refund':
                              bpoint_total = bpoint_total - Decimal(i.amount)


                 print (bpoint_total)
                 print ("Calculation Invoice Settlemnt Oracle Totals")

                 invoices = Invoice.objects.filter(settlement_date=today)
                 for i in invoices:
                     #print (i.reference)
                     invoice_total = invoice_total + Decimal(i.amount)
                     #print (i.order)
                     for ol in Order.objects.get(number=i.order_number).lines.all():
                          for order_total in ol.payment_details['order']:
                              oracle_total = oracle_total + Decimal(ol.payment_details['order'][order_total])
                              #print (Decimal(ol.payment_details['order'][order_total]))
                              #print (oracle_total)
                 print ("ORACLE TOTAL")
                 print (oracle_total)
                 print (invoice_total)

                 if bpoint_total != oracle_total:
                      raise ValidationError("Bpoint and Oracle Totals do not match. Bpoint Total: "+str(bpoint_total)+" Oracle Total: "+str(oracle_total))
            except Exception as e:
                 print ("Error: Sending Email Notification: "+settings.NOTIFICATION_EMAIL)
                 context = {
                     'error_report' : str(e)
                 }
                 email_list = []
                 for email_to in settings.NOTIFICATION_EMAIL.split(","):
                        email_list.append(email_to)
                 sendHtmlEmail(tuple(email_list),"[MOORING] oracle and bpoint total mistatch",context,'mooring/email/oracle_bpoint.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)
