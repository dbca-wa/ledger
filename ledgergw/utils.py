from ledger.payments.utils import oracle_parser_on_invoice,update_payments
from ledger.payments import models as ledger_payment_models #OracleInterfaceSystem
import re
from oscar.core.loading import get_class
from ledger.basket.models import Basket
from django.conf import settings
from ledger.api import models as ledgerapi_models
from ledger.order import utils  as order_utils
from ledger.payments.models import Invoice
from ledger.order.models import Order, Line as OrderLine
from ledger.payments.utils import isLedgerURL, systemid_check, LinkedInvoiceCreate
from ledger.payments.bpay.crn import getCRN
#from ledgergw import utils as ledgergw_utils
import requests
import base64
import json

def oracle_integration(date,override, system, system_name):
    oracle_codes = oracle_parser_on_invoice(date,system,system_name,override=override)

def generate_oracle_receipts(date, override, system):

    #today = datetime.today()
    #yesterday = today - timedelta(days=1)
    #print (yesterday.date().strftime('%Y-%m-%d'))
    ois = ledger_payment_models.OracleInterfaceSystem.objects.filter(integration_type='bpoint_api', enabled=True)
    for s in ois:
        print (s.system_id)
        oracle_integration(date, False, s.system_id,s.system_name)
    
def remove_html_tags(text):
    HTML_TAGS_WRAPPED = re.compile(r'<[^>]+>.+</[^>]+>')
    HTML_TAGS_NO_WRAPPED = re.compile(r'<[^>]+>')

    text = HTML_TAGS_WRAPPED.sub('', text)
    text = HTML_TAGS_NO_WRAPPED.sub('', text)
    return text

def build_basic_auth(username: str, merchant: str, password: str) -> str:
    """
    Build Authorization header value:
    Basic base64("username|merchant:password")
    """
    raw = f"{username}|{merchant}:{password}".encode("utf-8")
    return "Basic " + base64.b64encode(raw).decode("ascii")

def get_hpp_payment_link(request, basket_id, system_url):

    try:     
        CheckoutSessionData = get_class('checkout.utils', 'CheckoutSessionData')
        checkout_session = CheckoutSessionData(request)

        cookie_key = settings.OSCAR_BASKET_COOKIE_OPEN

        try:
            basket = Basket.objects.get(pk=basket_id)

            if not (basket.status == Basket.OPEN or basket.status == Basket.FROZEN or basket.status == Basket.SAVED):
                raise ValueError("Basket status is not valid")
            
            basket_total = str(basket.total_incl_tax).replace(".","")
        except Exception as e:
            print (e)

        if request.COOKIES.get('payment_api_wrapper') == 'true':
            if 'LEDGER_API_KEY' in request.COOKIES:
                apikey = request.COOKIES['LEDGER_API_KEY']
                if ledgerapi_models.API.objects.filter(api_key=apikey,active=1).count():
                    PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE = request.POST.get('PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE','')
                    PAYMENT_INTERFACE_SYSTEM_ID = request.POST.get('PAYMENT_INTERFACE_SYSTEM_ID','')
                    ois = ledger_payment_models.OracleInterfaceSystem.objects.get(id=int(PAYMENT_INTERFACE_SYSTEM_ID), system_id=PAYMENT_INTERFACE_SYSTEM_PROJECT_CODE) 

                    # Create auth key 
                    username = ois.bpoint_username
                    password = ois.bpoint_password
                    merchant = ois.bpoint_merchant_num
                    biller_code = ois.bpoint_biller_code  
                    currency = ois.bpoint_currency   

                    ci = order_utils.CreateOrderFromBasket()                     
                    if ois.system_id:
                        ci.system = ois.system_id
                        order_lookup = Order.objects.filter(basket_id=basket.id)
                        if order_lookup.count() > 0:
                            if Invoice.objects.filter(order_number=order_lookup[0].number).count() > 0:
                                pass     
                                # Required so we dont break invoice that generated as part of future payments
                                order = order_lookup[0]     
                            else:
                                # only recreate order for basket where basket data could change.  eg a booking site
                                OrderLine.objects.filter(order=order_lookup[0]).delete()
                                Order.objects.filter(basket_id=basket.id).delete()                                
                                order  = ci.create_order_from_basket(basket, total=None, shipping_method='No shipping required',shipping_charge=False, user=basket.owner, status='Frozen')      
                        else:
                            # no order exist,  create it
                            order  = ci.create_order_from_basket(basket, total=None, shipping_method='No shipping required',shipping_charge=False, user=basket.owner, status='Frozen')      
                    crn_string = '{0}{1}'.format(systemid_check(ois.system_id),order.number)
                    invoice_reference = getCRN(crn_string)     

                    if "?" in checkout_session.return_preload_url():
                        basket.notification_url = checkout_session.return_preload_url() + "&invoice="+invoice_reference
                    else:    
                        basket.notification_url = checkout_session.return_preload_url() + "?invoice="+invoice_reference

                    basket.success_return_url = system_url + "/ledger-ui/token-payment-success"
                    basket.save()

                    missing = [k for k,v in {
                        "BPOINT_USERNAME": username,
                        "BPOINT_PASSWORD": password,
                        "BPOINT_MERCHANT": merchant,
                        "BPOINT_BILLER_CODE": biller_code,
                    }.items() if not v]
                    if missing:
                        raise ValueError("Missing required environment variables")

                    auth_header = build_basic_auth(username, merchant, password)
                    
                    authkeyurl = settings.BPOINT_HPP_BASE_URL+"/txns/authkeys"
                    headers = {
                        "Authorization": auth_header,
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    }

                    payload = {}            
                    resp = requests.post(authkeyurl, headers=headers, data=json.dumps(payload), timeout=30)
                    
                    try:
                        data = resp.json()
                    except Exception:
                        data = {"raw": resp.text}

                    if not resp.ok:
                        raise RuntimeError(
                            f"Create Payment Request failed (HTTP {resp.status_code}): {data}"
                        )

                    authkey = data.get('authkey')
                    ## Create transaction details
                    attachtransdetailsurl = settings.BPOINT_HPP_BASE_URL+"/txns/authkeys/{}/txn-details".format(authkey)
                    payload ={
                            "action": "Payment",
                            "type": "Internet",
                            "subType": "Single",
                            "amount": basket_total,
                            "billerCode": biller_code,
                            "crn1" : invoice_reference,
                            "crn2": basket.booking_reference,                                        
                            "merchantReference": basket.basket_token,
                            "currency": currency,
                            "bypass3ds": False,
                            # "tokenisationMode": "Default",
                            # "emailAddress": basket.owner.email,
                            "storeCard": True,
                            "testMode": ois.bpoint_test,                                    
                                "tokenisationMode": "OptIn" # or None when not logged in
                            }
                    resp = requests.put(attachtransdetailsurl, headers=headers, data=json.dumps(payload), timeout=30)
                    
                    try:
                        data = resp.json()
                    except Exception:
                        data = {"raw": resp.text}

                    if not resp.ok:
                        raise RuntimeError(
                            f"Create Payment Request failed (HTTP {resp.status_code}): {data}"
                        )

                    attach_hpp_config_url = settings.BPOINT_HPP_BASE_URL+"/txns/authkeys/{}/hpp-configuration-with-webhook".format(authkey)
                    payload ={
                        "redirectionUrl": settings.BPOINT_REDIRECT_URL+"/ledger/payments/payment-triage/{}/".format(basket.basket_token),
                        "tokeniseTxnCheckBoxDefaultValue": False,
                        "hideCRN1": True,
                        # "hideCRN2": False,
                        # "hideCRN3": False,
                        "hideBillerCode": True,
                        # "returnBarLabel": "Go Back",
                        # "returnBarUrl": "https://xxx.dbca.wa.gov.au/api/test",
                        "webhook": {
                            "url": settings.BPOINT_WEBHOOK_URL+"/ledger/payments/api/bpoint-webhook/payment-success/{}/".format(basket.basket_token),                                                                                
                            "version": "5"
                            } 
                        }
                    resp = requests.put(attach_hpp_config_url, headers=headers, data=json.dumps(payload), timeout=30)
                    
                    try:
                        data = resp.json()
                    except Exception:
                        data = {"raw": resp.text}
                                                
                    if not resp.ok:
                        raise RuntimeError(
                            f"Create Payment Request failed (HTTP {resp.status_code}): {data}"
                        )

                    return data

    except Exception as e:
        print(e)

    