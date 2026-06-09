from django.conf import settings

from django.utils import timezone

import base64
import requests
import datetime
import json


def convert_amount(amount):
    '''
        Convert amount from bpoint format
        to normal currency format.
    '''
    return amount/100.0

def build_basic_auth(username, merchant, password):
    """
    Build Authorization header value:
      Basic base64("username|merchant:password")
    """
    raw = f"{username}|{merchant}:{password}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")

def refund_transaction(ois, originalTxnNumber,amount,crn1):
    base_url = settings.BPOINT_HPP_BASE_URL
    auth_header = build_basic_auth(ois.bpoint_username, ois.bpoint_merchant_num, ois.bpoint_password)

    url = f"{base_url}/txns"
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    amount = str(amount).replace(".","")
    payload ={
            "action": "Refund",
            "type": "TelephoneOrder",
            "subType": "Single",
            "crn1" : crn1,
            "amount": amount,
            "billerCode": ois.bpoint_biller_code,            
            "currency": ois.bpoint_currency,            
            "originalTxnNumber": originalTxnNumber,
            "testMode": ois.bpoint_test,  
            "tokenisationMode": "All"      
            }
            

    
    resp = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)
    
    try:
        data = resp.json()
    except Exception:
        data = {"raw": resp.text}

    if not resp.ok:
        raise RuntimeError(
            f"Create Payment Request failed (HTTP {resp.status_code}): {data}"
        )     

    card_type = None
    if data["paymentMethod"]["card"]["scheme"] == 'Mastercard':
        card_type="MC"
    if data["paymentMethod"]["card"]["scheme"] == 'Visa':
        card_type="VC"        
    txn = None

    settlement_date = data['settlementDate']
    processed = data['processedDateTime']
    
    if settlement_date:
        settlement_date=datetime.datetime.strptime(settlement_date, '%Y%m%d').date()
    if processed:        
        # processed=timezone('Australia/Sydney').localize(datetime.datetime.strptime(processed[:26], "%Y-%m-%dT%H:%M:%S.%f"))
        processed = data['processedDateTime']
        processed_date_time_obj = datetime.datetime.fromisoformat(processed)        
    try:
        from ledger.payments.models import BpointTransaction
        
        txn = BpointTransaction.objects.create(
            action=data["action"].lower(),
            crn1=crn1,
            original_crn1=crn1,
            amount=convert_amount(data["amount"]),
            amount_original=convert_amount(data["amountOriginal"]),
            amount_surcharge=convert_amount(data["amountSurcharge"]),
            type=data['type'],
            cardtype=card_type,
            response_code=data["responseCode"],
            receipt_number=data["receiptNumber"],
            response_txt=data["responseText"],
            processed=processed_date_time_obj,
            settlement_date=settlement_date,
            txn_number=data["txnNumber"],
            dvtoken=None,
            is_test=data["isTestTxn"],
            original_txn=data["originalTxnNumber"],
            last_digits=None
        )
    except Exception as e:
        raise
    return txn



