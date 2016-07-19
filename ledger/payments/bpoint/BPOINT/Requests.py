'''
Created on 15 Jan 2015

@author: ChrisR
'''
from abc import abstractmethod
from ledger.payments.bpoint.BPOINT.Utils import RequestSender
from ledger.payments.bpoint.BPOINT.Responses import TransactionResponse,\
    TransactionSearchResponse, AuthKeyResponse, DVTokenResponse,\
    DVTokenSearchResponse, APIResponse, FraudScreeningResponse

class Request(object):
    def __init__(self, credentials):
        self.url = None
        self.credentials = credentials
        self.method = None
        self.base_url = "https://www.bpoint.com.au/webapi/v2"
        self.user_agent = "BPOINT:1037:1|PYTHON"
        self.timeout = 100000
        
    @abstractmethod
    def get_payload(self):
        pass
    
    def build_url(self):
        return self.url
    
    def submit(self):
        req = RequestSender(self.base_url)
        return req.send(self)
    
class CrnBlock(object):
    def __init__(self):
        self.crn1 = None
        self.crn2 = None
        self.crn3 = None
        
    def get_crn_payload(self):
        return {"Crn1" : self.crn1, "Crn2" : self.crn2, "Crn3" : self.crn3}
    

class TransactionRequest(CrnBlock, Request):
    def __init__(self, credentials):
        Request.__init__(self, credentials)
        CrnBlock.__init__(self)
        self.amount = 0
        self.amount_original = 0
        self.amount_surcharge = 0
        self.action = None
        self.currency = None
        self.customer = None
        self.merchant_reference = None
        self.order = None
        self.original_txn_number = None
        self.biller_code = None
        self.store_card = False
        self.sub_type = None
        self.type = None
        self.card_details = None
        self.url = "/txns/"
        self.method = "POST"
        self.test_mode = False
        self.tokenisation_mode = 0
        self.email_address = None
        self.fraud_screening_request = None
        
    @abstractmethod
    def get_payload(self):
        payload = {}
        payload["Amount"] = self.amount
        payload["Action"] = self.action
        payload["AmountOriginal"] = self.amount_original
        payload["AmountSurcharge"] = self.amount_surcharge
        payload["Currency"] = self.currency
        payload["MerchantReference"] = self.merchant_reference
        payload["OriginalTxnNumber"] = self.original_txn_number
        payload["BillerCode"] = self.biller_code
        payload["StoreCard"] = self.store_card
        payload["SubType"] = self.sub_type
        payload["Type"] = self.type
        payload["TestMode"] = self.test_mode
        payload["TokenisationMode"] = self.tokenisation_mode
        payload["EmailAddress"] = self.email_address
        if self.customer is not None:
            payload["Customer"] = self.customer.get_payload()
        if self.order is not None:
            payload["Order"] = self.order.get_payload()
        payload.update(self.get_crn_payload())
        if self.card_details is not None:
            payload.update(self.card_details.get_card_payload())
        if self.fraud_screening_request is not None:
            payload["FraudScreeningRequest"] = self.fraud_screening_request.get_payload()
        return {"TxnReq" : payload}
    
    def submit(self):
        result = Request.submit(self)
        return TransactionResponse(result)
        
class Credentials(object):
    def __init__(self, username, password, merchant_number):
        self.username = username
        self.password = password
        self.merchant_number = merchant_number
        
class SystemStatusRequest(Request):
    def __init__(self, credentials):
        Request.__init__(self, credentials)

        self.url = "/status"
        self.method = "GET"
        
    def submit(self):
        return APIResponse(full_response_dict = Request.submit(self))
        
class TransactionSearchRequest(Request, CrnBlock):
    def __init__(self, credentials):
        Request.__init__(self, credentials)
        CrnBlock.__init__(self)
        
        self.url = "/txns/search"
        self.method = "POST"
        
        self.action = None
        self.amount = 0
        self.authorise_id = None
        self.bank_response_code = None
        self.card_type = None
        self.currency = None
        self.expiry_date = None
        self.from_date = None
        self.merchant_reference = None
        self.masked_card_number = None
        self.rrn = None
        self.receipt_number = None
        self.response_code = None
        self.biller_code = None
        self.settlement_date = None
        self.source = None
        self.to_date = None
        self.txn_number = None
        
    @abstractmethod
    def get_payload(self):
        payload = {}
        payload["Action"] = self.action
        payload["Amount"] = self.amount
        payload["AuthoriseId"] = self.authorise_id
        payload["BankResponseCode"] = self.bank_response_code
        payload["CardType"] = self.card_type
        payload["Currency"] = self.currency
        payload["ExpiryDate"] = self.expiry_date
        payload["FromDate"] = self.from_date
        payload["MerchantReference"] = self.merchant_reference
        payload["MaskedCardNumber"] = self.masked_card_number
        payload["RRN"] = self.rrn
        payload["ReceiptNumber"] = self.receipt_number
        payload.update(self.get_crn_payload())
        payload["ResponseCode"] = self.response_code
        payload["BillerCode"] = self.biller_code
        payload["SettlementDate"] = self.settlement_date
        payload["Source"] = self.source
        payload["ToDate"] = self.to_date
        payload["TxnNumber"] = self.txn_number
        
        return {"SearchInput" : payload}
        
    def submit(self):
        result = Request.submit(self)
        
        return TransactionSearchResponse(result)
        
class TransactionAuthKeyRequest(Request, CrnBlock):
    def __init__(self, credentials):
        Request.__init__(self, credentials)
        CrnBlock.__init__(self)
        
        self.url = "/txns/processtxnauthkey"
        self.method = "POST"
        
        self.hpp_parameters = None
        self.amount = 0
        self.amount_original = 0
        self.amount_surcharge = 0
        self.action = None
        self.customer = None
        self.biller_code = None
        self.currency = None
        self.merchant_reference = None
        self.order = None
        self.redirection_url = None
        self.test_mode = False
        self.webhook_url = None
        self.email_address = None
        self.tokenisation_mode = 0
        self.type = None
        self.sub_type = None
        self.fraud_screening_device_fingerprint = None
        self.amex_express_checkout = False
        
    @abstractmethod
    def get_payload(self):
        payload = {}
        if self.hpp_parameters is not None:
            payload["HppParameters"] = self.hpp_parameters.get_payload()
        payload["Action"] = self.action
        payload["Amount"] = self.amount
        payload["AmountOriginal"] = self.amount_original
        payload["AmountSurcharge"] = self.amount_surcharge
        payload["Currency"] = self.currency
        payload["MerchantReference"] = self.merchant_reference
        payload.update(self.get_crn_payload())
        payload["BillerCode"] = self.biller_code
        payload["TestMode"] = self.test_mode
        payload["TokenisationMode"] = self.tokenisation_mode
        payload["EmailAddress"] = self.email_address
        
        payload["Type"] = self.type
        payload["SubType"] = self.sub_type
        if self.customer is not None:
            payload["Customer"] = self.customer.get_payload()
        if self.order is not None:
            payload["Order"] = self.order.get_payload()
        if self.fraud_screening_device_fingerprint is not None:
            payload["FraudScreeningDeviceFingerPrint"] = self.fraud_screening_device_fingerprint
        
        payload["AmexExpressCheckout"] = self.amex_express_checkout
        
        wrapped_payload = {"ProcessTxnData" : payload}
        wrapped_payload["RedirectionUrl"] = self.redirection_url
        wrapped_payload["WebHookUrl"] = self.webhook_url
        
        return wrapped_payload
        
    def submit(self):
        result = Request.submit(self)
        
        return AuthKeyResponse(result)
    
class TransactionResultKeyRequest(Request):
    def __init__(self, credentials, result_key):
        Request.__init__(self, credentials)
        
        self.url = "/txns/withauthkey/" + result_key
        self.method = "GET"
        
    @abstractmethod
    def get_payload(self):
        return None
    
    def submit(self):
        result = Request.submit(self)
        
        return TransactionResponse(result)
    
class TransactionResultRequest(Request):
    def __init__(self, credentials, txn_number):
        Request.__init__(self, credentials)
        
        self.url = "/txns/" + str(txn_number)
        self.method = "GET"
        
    @abstractmethod
    def get_payload(self):
        return None
    
    def submit(self):
        result = Request.submit(self)
    
        return TransactionResponse(result)
    
class AddDVTokenRequest(Request, CrnBlock):
    def __init__(self, credentials):
        Request.__init__(self, credentials)
        CrnBlock.__init__(self)
        
        self.url = "/dvtokens"
        self.method = "POST"
        
        self.bank_account_details = None
        self.card_details = None
        self.email_address = None
        
        return
        
    @abstractmethod
    def get_payload(self):
        payload = {}
        if self.bank_account_details is not None:
            payload.update(self.bank_account_details.get_payload())
        if self.card_details is not None:
            payload.update(self.card_details.get_payload())
        payload["EmailAddress"] = self.email_address
        payload.update(self.get_crn_payload()) 
        
        return {"DVTokenReq" : payload}
        
    def submit(self):
        result = Request.submit(self)
        
        return DVTokenResponse(result)
        
class UpdateDVTokenRequest(AddDVTokenRequest):
    def __init__(self, credentials, token):
        AddDVTokenRequest.__init__(self, credentials)
        
        self.url = "/dvtokens/" + token
        self.method = "PUT"
        
        return
    
    @abstractmethod
    def get_payload(self):
        return AddDVTokenRequest.get_payload(self)
        
    def submit(self):
        return AddDVTokenRequest.submit(self)
    
class TokeniseTransactionRequest(Request):
    def __init__(self, credentials, txn_number):
        Request.__init__(self, credentials)
        self.url = "/dvtokens/txn/" + str(txn_number)
        self.method = "POST"
        
        return
    
    @abstractmethod
    def get_payload(self):
        return None
    
    def submit(self):
        result = Request.submit(self)
        
        return DVTokenResponse(result)

class DVTokenRetrievalRequest(Request):
    def __init__(self, credentials, token):
        Request.__init__(self, credentials)
        self.url = "/dvtokens/" + str(token)
        self.method = "GET"
        
        return
    
    @abstractmethod
    def get_payload(self):
        return None
    
    def submit(self):
        return DVTokenResponse(Request.submit(self))

class DVTokenSearchRequest(Request, CrnBlock):
    def __init__(self, credentials):
        Request.__init__(self, credentials)
        CrnBlock.__init__(self)
        
        self.method = "POST"
        self.url = "/dvtokens/search"
        
        self.card_type = None
        self.expired_cards_only = False
        self.expiry_date = None
        self.from_date = None
        self.masked_card_number = None
        self.source = None
        self.to_date = None
        self.dvtoken = None
        self.user_created = None
        self.user_updated = None
        
    @abstractmethod
    def get_payload(self):
        payload = {}
        payload["CardType"] = self.card_type
        payload["ExpiredCardsOnly"] = self.expired_cards_only
        payload["ExpiryDate"] = self.expiry_date
        payload["FromDate"] = self.from_date
        payload["MaskedCardNumber"] = self.masked_card_number
        payload["Source"] = self.source
        payload["ToDate"] = self.to_date
        payload["DVToken"] = self.dvtoken
        payload["UserUpdated"] = self.user_updated
        payload["UserCreated"] = self.user_created
        payload.update(self.get_crn_payload())
        
        return { "SearchInput" : payload }
    
    def submit(self):
        return DVTokenSearchResponse(Request.submit(self))        

class DeleteDVTokenRequest(Request):
    def __init__(self, credentials, token):
        Request.__init__(self, credentials)
        
        self.url = "/dvtokens/" + str(token)
        self.method = "DELETE"
        
        return
    
    @abstractmethod
    def get_payload(self):
        return None
    
    def submit(self):
        return APIResponse(full_response_dict = Request.submit(self))
    
class AddDVTokenAuthKeyRequest(Request, CrnBlock):
    def __init__(self, credentials):
        Request.__init__(self, credentials)
        CrnBlock.__init__(self)

        self.url = "/dvtokens/adddvtokenauthkey"
        self.method = "POST"
        
        self.email_address = None
        self.redirection_url = None
        self.webhook_url = None
        self.hpp_parameters = None
        
        return
    
    @abstractmethod
    def get_payload(self):
        payload = {}
        payload.update(self.get_crn_payload())
        payload["EmailAddress"] = self.email_address
        outer_payload = {}
        outer_payload["FixedAddDVTokenData"] = payload
        outer_payload["RedirectionUrl"] = self.redirection_url
        outer_payload["WebHookUrl"] = self.webhook_url
        if self.hpp_parameters is not None:
            outer_payload["HppParameters"] = self.hpp_parameters.get_payload()
            
        return outer_payload
        
    def submit(self):
        return AuthKeyResponse(Request.submit(self))
    
class UpdateDVTokenAuthKeyRequest(AddDVTokenAuthKeyRequest):
    def __init__(self, credentials, dvtoken):
        AddDVTokenAuthKeyRequest.__init__(self, credentials)
        self.dvtoken = dvtoken
        
        self.url = "/dvtokens/updatedvtokenauthkey"
        self.method = "POST"
        
        return
    
    @abstractmethod
    def get_payload(self):
        temp_payload = AddDVTokenAuthKeyRequest.get_payload(self)
        
        payload = {}
        payload["FixedUpdateDVTokenData"] = temp_payload["FixedAddDVTokenData"]
        payload["RedirectionUrl"] = temp_payload["RedirectionUrl"]
        payload["WebHookUrl"] = temp_payload["WebHookUrl"]
        if "HppParameters" in temp_payload:
            payload["HppParameters"] = temp_payload["HppParameters"] 
        
        payload["FixedUpdateDVTokenData"]["DVToken"] = self.dvtoken
        return payload
    
    def submit(self):
        return AuthKeyResponse(Request.submit(self))
        
class DVTokenResultKeyRequest(Request):
    def __init__(self, credentials, result_key):
        Request.__init__(self, credentials)
        
        self.method = "GET"
        self.url = "/dvtokens/withauthkey/" + result_key
        
        return
    
    @abstractmethod
    def get_payload(self):
        return None
    
    def submit(self):
        return AuthKeyResponse(Request.submit(self))
    
class HppTxnFlowParameters():
    def __init__(self):
        self.tokenise_txn_check_box_default_value = False
        
    def get_payload(self):
        payload = {}
        payload["TokeniseTxnCheckBoxDefaultValue"] = self.tokenise_txn_check_box_default_value
        
        return payload
        
class HppParameters():
    def __init__(self):
        self.hide_crn1 = False
        self.hide_crn2 = False
        self.hide_crn3 = False
        self.is_eddr = False
        self.crn1_label = None
        self.crn2_label = None
        self.crn3_label = None
        self.biller_code = None
        self.show_customer_details_form = False
        
    def get_payload(self):
        payload = {
            "HideCrn1" : self.hide_crn1,
            "HideCrn2" : self.hide_crn2,
            "HideCrn3" : self.hide_crn3,
            "IsEddr" : self.is_eddr,
            "Crn1Label" : self.crn1_label,
            "Crn2Label" : self.crn2_label,
            "Crn3Label" : self.crn3_label,
            "BillerCode" : self.biller_code,
            "ShowCustomerDetailsForm" : self.show_customer_details_form
            }
        return payload
        
class Customer(object):
    def __init__(self):
        self.address = None
        self.contact_details = None
        self.customer_number = None
        self.personal_details = None
        self.is_existing_customer = False
        self.days_on_file = 0
        
    def get_payload(self):
        payload = {}
        payload["CustomerNumber"] = self.customer_number
        payload["IsExistingCustomer"] = self.is_existing_customer
        payload["DaysOnFile"] = self.days_on_file
        if self.address is not None:
            payload["Address"] = self.address.get_payload()
        if self.contact_details is not None:
            payload["ContactDetails"] = self.contact_details.get_payload()
        if self.personal_details is not None:
            payload["PersonalDetails"] = self.personal_details.get_payload()
        
        return payload
        
class PersonalDetails(object):
    def __init__(self):
        self.date_of_birth = None
        self.first_name = None
        self.last_name = None
        self.middle_name = None
        self.salutation = None
        
    def get_payload(self):
        payload = { 
            "DateOfBirth" : self.date_of_birth,
            "FirstName" : self.first_name,
            "LastName" : self.last_name,
            "MiddleName" : self.middle_name,
            "Salutation" : self.salutation
        }
        return payload
        
class ContactDetails(object):
    def __init__(self):
        self.email_address = None
        self.fax_number = None
        self.home_phone_number = None
        self.mobile_phone_number = None
        self.work_phone_number = None
        
    def get_payload(self):
        payload = { 
            "EmailAddress" : self.email_address,
            "FaxNumber" : self.fax_number,
            "HomePhoneNumber" : self.home_phone_number,
            "MobilePhoneNumber" : self.mobile_phone_number,
            "WorkPhoneNumber" : self.work_phone_number
        }
        return payload
        
class Address(object):
    def __init__(self):
        self.address_line1 = None
        self.address_line2 = None
        self.address_line3 = None
        self.city = None
        self.country_code = None
        self.post_code = None
        self.state = None
    def get_payload(self):
        payload = {
            "AddressLine1" : self.address_line1,
            "AddressLine2" : self.address_line2,
            "AddressLine3" : self.address_line3,
            "City" : self.city,
            "CountryCode" : self.country_code,
            "PostCode" : self.post_code,
            "State" : self.state
        }
        return payload
        
class Order(object):
    def __init__(self):
        self.billing_address = None
        self.shipping_address = None
        self.shipping_method = None
        self.order_recipients = None
        self.order_items = None
        
    def get_payload(self):
        payload = {}
        payload["ShippingMethod"] = self.shipping_method
        payload["OrderRecipients"] = self.order_recipients
        payload["OrderItems"] = self.order_items
        if self.billing_address is not None:
            payload["BillingAddress"] = self.billing_address.get_payload()
        if self.shipping_address is not None:
            payload["ShippingAddress"] = self.shipping_address.get_payload()
        
        return payload
        
class OrderAddress(object):
    def __init__(self):
        self.address = None
        self.contact_details = None
        self.personal_details = None
        
    def get_payload(self):
        payload = {}
        if self.address is not None:
            payload["Address"] = self.address.get_payload()
        if self.contact_details is not None:
            payload["ContactDetails"] = self.contact_details.get_payload()
        if self.personal_details is not None:
            payload["PersonalDetails"] = self.personal_details.get_payload()
            
        return payload
        
class OrderItem(object):
    def __init__(self):
        self.comments = None
        self.description = None
        self.gift_message = None
        self.part_number = None
        self.product_code = None
        self.quantity = None
        self.sku = None
        self.shipping_method = None
        self.shipping_number = None
        self.unit_price = None
        
    def get_payload(self):
        payload = {
            "Comments" : self.comments,
            "Description" : self.description,
            "GiftMessage" : self.gift_message,
            "PartNumber" : self.part_number,
            "ProductCode" : self.product_code,
            "Quantity" : self.quantity,
            "SKU" : self.sku,
            "ShippingMethod" : self.shipping_method,
            "ShippingNumber" : self.shipping_number,
            "UnitPrice" : self.unit_price
        }
        return payload
        
class OrderRecipient(object):
    def __init__(self):
        self.address = None
        self.contact_details = None
        self.personal_details = None
        
    def get_payload(self):
        payload = {}
        if self.address is not None:
            payload["Address"] = self.address.get_payload()
        if self.contact_details is not None:
            payload["ContactDetails"] = self.contact_details.get_payload()
        if self.personal_details is not None:
            payload["PersonalDetails"] = self.personal_details.get_payload()
        
        return payload
        
class CustomField():
    def __init__(self):
        self.custom_field_value = None
        
    def get_payload(self):
        payload = {
            "CustomFieldValue" : self.custom_field_value
        }
        return payload
        
class FraudScreeningRequest(object):
    def __init__(self):
        self.perform_fraud_screening = False
        self.device_fingerprint = None
        self.customer_ip_address = None
        self.txn_source_website_url = None
        self.custom_field = None
        
    def get_payload(self):
        payload = {
            "PerformFraudScreening" : self.perform_fraud_screening,
            "DeviceFingerPrint" : self.device_fingerprint,
            "CustomerIPAddress" : self.customer_ip_address,
            "TxnSourceWebsiteURL" : self.txn_source_website_url,
            "CustomField" : self.custom_field
        }
        return payload
