from django.core.management.base import BaseCommand, CommandError
from ledger.address.models import UserAddress
from django.core.exceptions import ValidationError
from confy import env, database
from ledger.accounts import models
from django.conf import settings
from ledger.emails.emails import sendHtmlEmail
from django.utils import timezone
from datetime import datetime, timedelta
import requests
import json

class Command(BaseCommand):
    help = 'Imports Active Directory Users into Ledger.'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        
        try:
            print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))+": Running Active Directory Sync")
            ACTIVE_DIRECTORY_JSON_URL=env('ACTIVE_DIRECTORY_JSON_URL',[])
            url = ACTIVE_DIRECTORY_JSON_URL 
            resp = requests.get(url, data ={})
            data = resp.json() 
            row =0 
            noaccount=0
            updatedaccount=0
            for user in data:
                if 'Mail' in user:

                   if user["Mail"] is not None:
                       if "@" in user["Mail"]: 
                           ed = str(user["Mail"]).split("@")
                           email_domain = ed[1]
                           if email_domain in settings.DEPT_DOMAINS:
                               if user:
                               #if row < 100:
                                 if user['AccountEnabled'] is True:
                                      email = user['Mail'].lower()
                                      first_name = user['GivenName']
                                      last_name = user['Surname']
                                      position_title = user['JobTitle']
                                      mobile = user['Mobile']
                                      phone = user['TelephoneNumber']
                                      fax  = user['FacsimileTelephoneNumber']
                                      manager_email = ''
                                      manager_name = ''
                                      if user['Manager']:
                                            if 'UserPrincipalName' in user['Manager']:
                                                manager_email = user['Manager']['UserPrincipalName']
                                            if 'DistinguishedName'  in user['Manager']:
                                                dn_clean = str(user['Manager']['DistinguishedName']).replace("\n", "")
                                                dn = dn_clean[3:].split(',OU=')
                                                manager_name=dn[0]
                                      if first_name is None or first_name == '':
                                            first_name = "No First Name"
                                      if last_name is None or last_name == '':
                                          last_name = "No Last Name"

                                      u_obj = models.EmailUser.objects.filter(email=email)
                                      if u_obj.count() > 0:
                                         u = u_obj[0]
                                         u.first_name = first_name
                                         u.last_name = last_name
                                         u.is_staff = True
                                         u.phone_number = phone
                                         u.mobile_number = mobile
                                         u.position_title = position_title
                                         u.manager_name = manager_name
                                         u.manager_email = manager_email
                                         u.fax_number = fax
                                         u.save()
                                         updatedaccount = updatedaccount + 1
                                      else:
                                         print ("Creating: "+email)
                                         models.EmailUser.objects.create(email=email,
                                                                         first_name=first_name,
                                                                         last_name=last_name,
                                                                         is_staff=True,
                                                                         phone_number=phone,
                                                                         mobile_number=mobile,
                                                                         position_title=position_title,
                                                                         manager_name=manager_name,
                                                                         manager_email=manager_email,
                                                                         fax_number=fax
                                                                         )

                                         print (email)
                                         noaccount = noaccount + 1
                                      row = row + 1
                                  
            
                
            print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))+": Successfully Completed Active Directory Import")
            print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))+": Created Accounts: "+str(noaccount))
            print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))+": Updated Accounts: "+str(updatedaccount))
        except Exception as e:
            time_error = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            print ("Active Directory Import Error")
            print (e)
            email_list = []
            context = {"ad_error": e,}
            for email_to in settings.NOTIFICATION_EMAIL.split(","):
                   email_list.append(email_to)
            sendHtmlEmail(tuple(email_list),"[LEDGER] Active Directory Account Sync "+time_error,context,'email/ledger_active_directory_sync.html',None,None,settings.EMAIL_FROM,'system-oim',attachments=None)

            #raise ValidationError(e)



