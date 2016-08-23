'''
Created on 16 Jan 2015

@author: ChrisR
'''
from ledger.payments.bpoint.BPOINT.Utils import CardDetails, BankAccountDetails

class Response(object):
    def __init__(self):
        pass
    
class CVNResult(object):
    def __init__(self, resp_dict):
        
        if resp_dict is not None:
            cvn_res_code = resp_dict.get("CVNResultCode")
            
            if cvn_res_code is not None:
                self.cvn_result_code = cvn_res_code
        return
        
class APIDetail(object):
    def __init__(self):
        self.response_code = None
        self.response_text = None
        
    
class APIResponse(Response):
    def __init__(self, api_response_dict = None, full_response_dict = None):
        assert(api_response_dict is not None or full_response_dict is not None)
        if api_response_dict is not None:
            response_dict = api_response_dict
        else:
            response_dict = full_response_dict["APIResponse"]
            
        self.api_response = APIDetail()
        
        self.api_response.response_code = response_dict["ResponseCode"]
        self.api_response.response_text = response_dict["ResponseText"]
        
        return
    
    def successful(self):
        return_val = False
        
        if self.api_response.response_code == "0":
            return_val = True
            
        return return_val

class TransactionResponse(APIResponse):
    def __init__(self, response_dict):
        if "APIResponse" in response_dict:
            APIResponse.__init__(self, full_response_dict = response_dict)
            
        if response_dict.get("TxnResp") is not None:
            tx_dict = response_dict["TxnResp"]
            self.action = tx_dict["Action"]
            self.amount = tx_dict["Amount"]
            self.amount_original = tx_dict["AmountOriginal"]
            self.amount_surcharge = tx_dict["AmountSurcharge"]
            self.threeds_response = ThreeDSResponse(tx_dict["ThreeDSResponse"])
            self.authorise_id = tx_dict["AuthoriseId"]
            self.bank_account_details = BankAccountDetails(dict_resp = tx_dict.get("BankAccountDetails"))
            self.bank_response_code = tx_dict["BankResponseCode"]
            self.cvn_result = CVNResult(tx_dict["CVNResult"])
            self.card_details = CardDetails(result_array = tx_dict["CardDetails"])
            self.card_type = tx_dict["CardType"]
            self.currency = tx_dict["Currency"]
            self.merchant_reference = tx_dict["MerchantReference"]
            self.is_threeds = tx_dict["IsThreeDS"]
            self.is_cvn_present = tx_dict["IsCVNPresent"]
            self.merchant_number = tx_dict["MerchantNumber"]
            self.original_txn_number = tx_dict["OriginalTxnNumber"]
            self.processed_date_time = tx_dict["ProcessedDateTime"]
            self.rrn = tx_dict["RRN"]
            self.receipt_number = tx_dict["ReceiptNumber"]
            self.crn1 = tx_dict["Crn1"]
            self.crn2 = tx_dict["Crn2"]
            self.crn3 = tx_dict["Crn3"]
            self.response_code = tx_dict["ResponseCode"]
            self.response_text = tx_dict["ResponseText"]
            self.biller_code = tx_dict["BillerCode"]
            self.settlement_date = tx_dict["SettlementDate"]
            self.source = tx_dict["Source"]
            self.store_card = tx_dict["StoreCard"]
            self.sub_type = tx_dict["SubType"]
            self.txn_number = tx_dict["TxnNumber"]
            self.is_test_txn = tx_dict["IsTestTxn"]
            self.type = tx_dict["Type"]
            self.dvtoken = tx_dict.get("DVToken")
            self.fraud_screening_response = FraudScreeningResponse(fraud_dict = tx_dict["FraudScreeningResponse"])
            
class TransactionSearchResponse(APIResponse):
    def __init__(self, response_dict):
        
        self.txn_resp_list = []
        
        if "APIResponse" in response_dict:
            APIResponse.__init__(self, full_response_dict = response_dict)
            
        tx_responses = response_dict["TxnRespList"]
        
        if tx_responses is not None:
            for i, txn in enumerate(tx_responses):
                self.txn_resp_list.append(TransactionResponse({"TxnResp" : txn}))
            
        return
            
class AuthKeyResponse(APIResponse):
    def __init__(self, response_dict):
        APIResponse.__init__(self, full_response_dict = response_dict)
        
        if "AuthKey" in response_dict:
            self.auth_key = response_dict["AuthKey"]
        else:
            self.auth_key = None
            
        return
    
class DVTokenResponse(APIResponse):
    def __init__(self, response_dict):
        if "APIResponse" in response_dict:
            APIResponse.__init__(self, full_response_dict = response_dict)
        
        dvtoken_dict = response_dict.get("DVTokenResp")
        
        if dvtoken_dict is not None:
            if "BankAccountDetails" in dvtoken_dict:
                self.bank_account_details = BankAccountDetails(dict_resp = dvtoken_dict["BankAccountDetails"])
            if "CardDetails" in dvtoken_dict:
                self.card_details = CardDetails(result_array = dvtoken_dict["CardDetails"])
            
            self.card_type = dvtoken_dict["CardType"]
            self.email_address = dvtoken_dict["EmailAddress"]
            self.crn1 = dvtoken_dict["Crn1"]
            self.crn2 = dvtoken_dict["Crn2"]
            self.crn3 = dvtoken_dict["Crn3"]
            self.dvtoken = dvtoken_dict["DVToken"]
        
        return
        
class DVTokenSearchResponse(APIResponse):
    def __init__(self, response_dict):
        self.dvtoken_resp_list = []
        if "APIResponse" in response_dict:
            APIResponse.__init__(self, full_response_dict = response_dict)
            
        if response_dict.get("DVTokenRespList") is not None:
            for i, dvtoken in enumerate(response_dict["DVTokenRespList"]):
                self.dvtoken_resp_list.append(DVTokenResponse({"DVTokenResp" : dvtoken}))
        
        return

class ThreeDSResponse(object):
    def __init__(self, resp_dict):
        if resp_dict is not None:
            self.eci = resp_dict["ECI"]
            self.enrolled = resp_dict["Enrolled"]
            self.status = resp_dict["Status"]
            self.verify_security_level = resp_dict["VerifySecurityLevel"]
            self.verify_status = resp_dict["VerifyStatus"]
            self.verify_dvtoken = resp_dict["VerifyDVToken"]
            self.verify_type = resp_dict["VerifyType"]
            self.xid = resp_dict["XID"]
        else:
            self.eci = None
            self.enrolled = None
            self.status = None
            self.verify_security_level = None
            self.verify_status = None
            self.verify_dvtoken = None
            self.verify_type = None
            self.xid = None
            
        return
        
class ReDResponse():
    def __init__(self, red_dict):
        if red_dict is not None:
            self.REQ_ID         =   red_dict.get("REQ_ID")
            self.ORD_ID         =   red_dict.get("ORD_ID")
            self.STAT_CD        =   red_dict.get("STAT_CD")
            self.FRAUD_STAT_CD  =   red_dict.get("FRAUD_STAT_CD")
            self.FRAUD_RSP_CD   =   red_dict.get("FRAUD_RSP_CD")
            self.FRAUD_REC_ID   =   red_dict.get("FRAUD_REC_ID")
            self.FRAUD_NEURAL   =   red_dict.get("FRAUD_NEURAL")
            self.FRAUD_RCF      =   red_dict.get("FRAUD_RCF")
        else:
            self.REQ_ID = None
            self.ORD_ID = None
            self.STAT_CD = None
            self.FRAUD_STAT_CD = None
            self.FRAUD_RSP_CD = None
            self.FRAUD_REC_ID = None
            self.FRAUD_NEURAL = None
            self.FRAUD_RCF = None
        return

class FraudScreeningResponse(object):
    def __init__(self, fraud_dict):
        if fraud_dict is not None:
            self.txn_rejected       =   fraud_dict["TxnRejected"]
            self.response_code      =   fraud_dict["ResponseCode"]
            self.response_message   =   fraud_dict["ResponseMessage"]
            self.red_response       =   ReDResponse(red_dict = fraud_dict.get("ReDResponse"))
        else:
            self.txn_rejected       = False
            self.response_code      = None
            self.response_message   = None
            self.red_response       = None
        return
