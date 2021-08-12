from django.core.cache import cache
from confy import env
import datetime
import hashlib


def bpoint_transaction_hash():
    change_hash = cache.get('BpointTransaction')
    if change_hash is None:
       change_hash = hashlib.md5(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S").encode('utf-8')).hexdigest()
       cache.set('BpointTransaction', change_hash,  86400)
    return change_hash

def bpay_transaction_hash():
    change_hash = cache.get('BpayTransaction')
    if change_hash is None:
         change_hash = hashlib.md5(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S").encode('utf-8')).hexdigest()
         cache.set('BpayTransaction', change_hash,  86400)
    return change_hash

def cash_transaction_hash():
    change_cash_hash = cache.get('CashTransaction')
    if change_cash_hash is None:
       change_cash_hash = hashlib.md5(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S").encode('utf-8')).hexdigest()
       cache.set('CashTransaction', change_cash_hash,  86400)
    return change_cash_hash
