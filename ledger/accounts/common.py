import requests
import json
from django.conf import settings
from django.core.cache import cache
from ledger.accounts import utils
from ledger.accounts.models import EmailUser

def retrieve_department_users():
    try:
        du_array = []
        department_users = EmailUser.objects.filter(is_staff=True)
        for du in department_users:
            if utils.in_dbca_domain(du):
                 row = {"pk":du.id,"name":du.get_full_name(),"preferred_name":du.first_name,"title":du.position_title,"email":du.email,"telephone":du.phone_number,"mobile_phone":du.mobile_number}
            du_array.append(row)
        return du_array
    except:
        raise

def get_department_user(email):
    try:
        department_users = []
        department_users = EmailUser.objects.filter(email=email)
        if department_users.count() > 0:
            if utils.in_dbca_domain(department_users[0]):
                row = {"pk":department_users[0].id,"name":department_users[0].get_full_name(),"preferred_name":department_users[0].first_name,"title":department_users[0].position_title,"email":department_users[0].email,"telephone":department_users[0].phone_number,"mobile_phone":department_users[0].mobile_number}
                return row
            else:
                return None
        else:
            return None
    except:
        raise

