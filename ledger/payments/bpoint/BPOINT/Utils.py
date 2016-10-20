'''
Created on 15 Jan 2015

@author: ChrisR
'''
import requests
import json
import base64

class RequestSender(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.user_agent = "Premier.Billpay.API.BPOINT.Python-V1.0";
        
    def send(self, request):
        credentials = request.credentials
        auth_header_value = base64.b64encode((credentials.username + "|" +
                                          credentials.merchant_number + ":" +
                                          credentials.password).encode())
        url = self.base_url + request.build_url()
        
        built_payload = request.get_payload()
        payload = None
        
        if built_payload is not None:
            payload = json.dumps(built_payload)
        
        method = request.method
        header_dict = {"Authorization" : auth_header_value.decode(), "Content-Type" : "application/json; charset=utf-8"}
        
        if request.user_agent is not None:
            header_dict["User-Agent"] = request.user_agent
        else:
            header_dict["User-Agent"] = self.user_agent
            
        if method == "POST":
            endpoint = requests.post(url, data = payload, headers = header_dict, timeout = request.timeout / 1000)
        elif method == "GET":
            endpoint = requests.get(url, headers = header_dict, timeout = request.timeout / 1000)
        elif method == "PUT":
            endpoint = requests.put(url, data = payload, headers = header_dict, timeout = request.timeout / 1000)
        elif method == "DELETE":
            endpoint = requests.delete(url, headers = header_dict, timeout = request.timeout / 1000)
        
        return json.loads(endpoint.text)

class WebHookConsumer:
    @staticmethod
    def consume_transaction(payload):
        return TransactionResponse(json.loads(payload))

    @staticmethod
    def consume_token(payload):
        return TokenResponse(json.loads(payload))
    
class CardDetails(object):
    def __init__(self, card_holder_name = None, card_number = None, expiry_date = None, 
                 cvn = None, masked_card_number = None, result_array = None):
        if result_array is not None:
            self.masked_card_number = result_array["MaskedCardNumber"]
            self.expiry_date = result_array["ExpiryDate"]
            if "CardHolderName" in result_array:
                self.card_holder_name = result_array["CardHolderName"]
            else:
                self.card_holder_name = None
        else:
            self.card_holder_name = card_holder_name
            self.card_number = card_number
            self.expiry_date = expiry_date
            self.cvn = cvn
            self.masked_card_number = masked_card_number
        
    def get_card_payload(self):
        inner_dict = {"CardHolderName" : self.card_holder_name,  
                          "ExpiryDate" : self.expiry_date, "Cvn" : self.cvn}
        if self.masked_card_number is None:
            inner_dict.update({"CardNumber" : self.card_number})
        else:
            inner_dict.update({"MaskedCardNumber" : self.masked_card_number})
            
        return {"CardDetails" : inner_dict}
    
    def get_payload(self):
        return self.get_card_payload()
    
class BankAccountDetails(object):
    def __init__(self, account_name = None, account_number = None, bsb_number = None,
                 truncated_account_number = None, dict_resp = None):
        
        if dict_resp is not None:
            self.account_name = dict_resp["AccountName"]
            self.account_number = dict_resp["AccountNumber"]
            self.bsb_number = dict_resp["BSBNumber"]
            self.truncated_account_number = dict_resp["TruncatedAccountNumber"]
        else:
            self.account_name = account_name
            self.account_number = account_number
            self.bsb_number = bsb_number
            self.truncated_account_number = truncated_account_number
            
        return
        
    def get_payload(self):
        payload = {"AccountNumber" : self.account_number,
                   "AccountName" : self.account_name,
                   "BSBNumber" : self.bsb_number}
        
        return {"BankAccountDetails" : payload}

