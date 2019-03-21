import requests
import json
from django.conf import settings
from django.core.cache import cache


def in_dbca_domain(user):
    domain = user.email.split('@')[1]
    if domain in settings.DEPT_DOMAINS:
        if not user.is_staff:
            # hack to reset department user to is_staff==True, if the user logged in externally (external departmentUser login defaults to is_staff=False)
            user.is_staff = True
            user.save()
        return True
    return False

def get_department_user_minimal(email):
    try:
        res = requests.get('{}/api/users/?minimal&email={}'.format(settings.CMS_URL,email), auth=(settings.LEDGER_USER,settings.LEDGER_PASS))
        res.raise_for_status()
        data = json.loads(res.content).get('objects')
        if len(data) > 0:
            user_obj = data[0]
            if 'org_data' in user_obj and 'cost_centre' in user_obj['org_data'] and user_obj['org_data']['cost_centre']:
                return user_obj
        return {}
    except:
        return {}

def get_department_user_compact(email):
    try:
        res = requests.get('{}/api/users/fast/?compact&email={}'.format(settings.CMS_URL,email), auth=(settings.LEDGER_USER,settings.LEDGER_PASS))
        res.raise_for_status()
        data = json.loads(res.content).get('objects')
        if len(data) > 0:
            user_obj = data[0]
            if 'org_data' in user_obj and 'cost_centre' in user_obj['org_data'] and user_obj['org_data']['cost_centre']:
                return user_obj
        return {}
    except:
        return {}


def get_app_label():
    try:
        return settings.SYSTEM_APP_LABEL
    except AttributeError:
        return ''
