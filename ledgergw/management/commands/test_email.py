from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from decimal import *
from ledgergw.emails import sendHtmlEmail
import json

from datetime import timedelta, datetime

class Command(BaseCommand):
    help = 'Check BPOINT Settlement dates with oracle Invoice Settlement dates to ensure totals match.'

    def handle(self, *args, **options):
            today = datetime.today()# - timedelta(days=3)
            system = settings.PS_PAYMENT_SYSTEM_ID
            system = system.replace('S','0')

            print ("Sending Email Notification to: "+settings.NOTIFICATION_EMAIL)
            context = {'test': 'test'
            }

            email_list = []
            for email_to in settings.NOTIFICATION_EMAIL.split(","):
                   email_list.append(email_to)
            sendHtmlEmail(tuple(email_list),"[LEDGER] Test Email",context,'ledgergw/email/test_email.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)



