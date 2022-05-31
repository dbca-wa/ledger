from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from ledger.payments import models as ledger_payment_models #OracleInterfaceSystem
from ledgergw import utils as ledgergw_utils
from decimal import *
from ledgergw.emails import sendHtmlEmail
import json
from datetime import timedelta, datetime

class Command(BaseCommand):
    help = 'Generate Oracle Receipts'

    def handle(self, *args, **options):
            today = datetime.today()# - timedelta(days=3)
            #system = settings.PS_PAYMENT_SYSTEM_ID
            #system = system.replace('S','0')
            yesterday = today - timedelta(days=1) 
            ledgergw_utils.generate_oracle_receipts(yesterday.date().strftime('%Y-%m-%d'), False, None)

            #print (yesterday.date().strftime('%Y-%m-%d'))
            #ois = ledger_payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api', enabled=True)
            #for s in ois:
            #    print (s.system_id)
            #    ledgergw_utils.oracle_integration(yesterday.date().strftime('%Y-%m-%d'), False, s.system_id)

