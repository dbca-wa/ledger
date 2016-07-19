import datetime
import decimal
from django.utils.translation import ugettext_lazy as _
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
from django.core.exceptions import ValidationError

from models import BpointTransaction
from gateway import Gateway
from ledger.payments.bpoint.BPOINT.API import CardDetails

from ledger.payments.bpoint import settings as bpoint_settings
from ledger.payments.invoice.models import Invoice

class Facade(object):
    """
        Bridge between oscars's objects and gateway object
    """
    def __init__(self):
        self.gateway = Gateway(
            bpoint_settings.BPOINT_USERNAME,
            bpoint_settings.BPOINT_PASSWORD,
            bpoint_settings.BPOINT_MERCHANT_NUM
        )
    
    def convert_amount(self,amount):
        '''
            Convert amount from bpoint format
            to normal currency format.
        '''
        return amount/100.0
    
    def _get_card_details(self, bankcard, request_source):
        '''
            Get card details from from applicable
            request sources
            Available sources are 'api' and 'checkout'
        '''
        if not request_source in ['checkout','api']:
            raise Exception('Please enter a valid request source.')
        
        if request_source == 'checkout':
            return CardDetails(
                card_number=bankcard.number,
                cvn=bankcard.ccv,
                expiry_date=bankcard.expiry_date.strftime("%m%y")
            )
        elif request_source == 'api':
            return CardDetails(
                card_number=bankcard.number,
                cvn=bankcard.cvn,
                expiry_date=bankcard.expiry
            )
    
    def _submit_info(self,order_number,reference,amount,action,_type,sub_type,request_source,bank_card=None,orig_txn_number=None):
        '''
            Submit the transaction info to the
            gateway
        '''
        res,card_details = None, None

        if bank_card:
            card_details = self._get_card_details(bank_card,request_source)
        if amount:
            amount = int(amount*100)
        res = self.gateway.handle_txn(order_number,reference,action,amount,card_details,
                                               bpoint_settings.BPOINT_BILLER_CODE,_type,sub_type,orig_txn_number)
        # Check if the transaction was successful
        if not res.api_response.response_code == 0:
            raise ValueError(res.api_response.response_text)
        
        return self._create_txn(
            res.action,
            res.crn1,
            res.amount,
            res.amount_original,
            res.amount_surcharge,
            res.type,
            res.card_type,
            res.receipt_number,
            res.response_code,
            res.response_text,
            res.processed_date_time,
            res.settlement_date,
            res.txn_number
        )

    def _create_txn(self,action,crn1,amount,amount_original,amount_surcharge,
                    type,cardtype,receipt_number,response_code,response_txt,processed,settlement_date,txn_number):
        '''
            Store a Bpoint Transaction object whether the bpoint
            transaction response was successful or not
        '''
        txn = None
        if settlement_date:
            settlement_date=datetime.datetime.strptime(settlement_date, '%Y%m%d').date()
        try:
            txn = BpointTransaction.objects.create(
                action=action,
                crn1=crn1,
                amount=self.convert_amount(amount),
                amount_original=self.convert_amount(amount_original),
                amount_surcharge=self.convert_amount(amount_surcharge),
                type=type,
                cardtype=cardtype,
                response_code=response_code,
                receipt_number=receipt_number,
                response_txt=response_txt,
                processed=processed,
                settlement_date=settlement_date,
                txn_number=txn_number
            )
        except Exception as e:
            raise
        return txn
    
    def fetch_transaction(self, txn_number):
        '''
            Fetch all the detials of a previously
            completed transaction
        '''
        res = self.gateway.get_txn(txn_number)
        
        if res.txn_resp_list:
            return res.txn_resp_list[0]
        
        return res.api_response
    
    def fetch_transactions(self):
        '''
            Fetch all transactions from bpoint
        '''
        self.gateway.get_txns()

    def post_transaction(self, action,_type,sub_type,request_source,order_number=None,reference=None,total=None,bankcard=None,orig_txn_number=None):
        '''Create a new transaction.
            Actions are:
            payment - Debit the card immediately
            preauth - Hold Funds in the card
            capture - Debit a card for a previousl created preauth transaction
            reversal - Reverses the orginal transaction
            refund - Credit funds back to the card
        '''
        try:
            if reference:
                inv = Invoice.objects.get(reference=reference)
                if inv.payment_status == 'paid':
                    raise ValidationError('This invoice has already been paid for.')
                if decimal.Decimal(total) > inv.balance:
                    raise ValidationError('The amount to be charged is more than the amount payable for this invoice.')
            txn = self._submit_info(order_number,reference,total,action,_type,sub_type,request_source,bankcard,orig_txn_number)
            self.friendly_error_msg(txn)
            
            return txn
        except Exception:
            raise
        
    def friendly_error_msg(self, txn):
        if not txn.approved:
            raise Exception(txn.response_txt)
        return False
    
