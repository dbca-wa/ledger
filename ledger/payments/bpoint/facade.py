import datetime
import decimal
from pytz import timezone
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from oscar.apps.payment.exceptions import UnableToTakePayment, InvalidGatewayRequestError
from django.core.exceptions import ValidationError

from ledger.payments.bpoint.models import BpointTransaction
from ledger.payments.bpoint.gateway import Gateway
from ledger.payments.bpoint.BPOINT.API import CardDetails

from ledger.payments.bpoint import settings as bpoint_settings

from ledger.payments.models import Invoice, BpointToken

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
    
    def _get_card_details(self, bankcard):
        '''
            Get card details from bankcard object
        '''
        return CardDetails(
            card_number=bankcard.number,
            cvn=bankcard.ccv,
            expiry_date=bankcard.expiry_date.strftime("%m%y") if bankcard.expiry_date else None
        )

    def _submit_info(self,order_number,reference,amount,action,_type,sub_type,bank_card=None,orig_txn_number=None):
        '''
            Submit the transaction info to the
            gateway
        '''
        res,card_details,bankcard_lastdigits = None, None, None
        if bank_card:
            card_details = self._get_card_details(bank_card)
        if amount:
            amount = int(amount*100)
        if bank_card.last_digits:
            bankcard_lastdigits = bank_card.last_digits
        # Handle any other exceptions that occur that are not from bpoint
        try:
            res = self.gateway.handle_txn(order_number,reference,action,amount,card_details,
                                               bpoint_settings.BPOINT_BILLER_CODE,_type,sub_type,orig_txn_number)
        except Exception:
            raise

        # Check if the transaction was successful
        if not res.api_response.response_code == 0:
            raise UnableToTakePayment(res.api_response.response_text)
        
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
            res.txn_number,
            res.dvtoken,
            res.is_test_txn,
            res.original_txn_number,
            bankcard_lastdigits
        )

    def _create_txn(self,action,crn1,amount,amount_original,amount_surcharge,
                    type,cardtype,receipt_number,response_code,response_txt,processed,settlement_date,txn_number,dvtoken,is_test,original_transaction,bankcard_lastdigits=None):
        '''
            Store a Bpoint Transaction object whether the bpoint
            transaction response was successful or not
        '''
        txn = None
        if settlement_date:
            settlement_date=datetime.datetime.strptime(settlement_date, '%Y%m%d').date()
        if processed:
            processed=timezone('Australia/Sydney').localize(datetime.datetime.strptime(processed[:26], "%Y-%m-%dT%H:%M:%S.%f"))
        try:
            txn = BpointTransaction.objects.create(
                action=action,
                crn1=crn1,
                original_crn1=crn1,
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
                txn_number=txn_number,
                dvtoken=dvtoken,
                is_test=is_test,
                original_txn=original_transaction,
                last_digits = bankcard_lastdigits
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

    def request_token(self,reference,bank_card=None):
        ''' Get a new DVToken
        '''
        res,card_details = None, None
        if bank_card:
            card_details = self._get_card_details(bank_card)
        # Handle any other exceptions that occur that are not from bpoint
        try:
            res = self.gateway.request_new_token(card_details,reference)
        except Exception as e:
            raise

        # Check if the transaction was successful
        if not res.api_response.response_code == 0:
            raise UnableToTakePayment(res.api_response.response_text)

        return res

    def post_transaction(self, action,_type,sub_type,order_number=None,reference=None,total=None,bankcard=None,orig_txn_number=None,replay=False):
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
                if not replay:
                    if action in ['reversal','refund'] and inv.payment_status == 'unpaid':
                        raise ValidationError("A {} cannot be made for an unpaid invoice.".format(action))
                    if action == 'refund' and (inv.payment_amount < decimal.Decimal(total)):
                        raise ValidationError("A refund greater than the amount paid for the invoice cannot be made.")
                    if inv.payment_status == 'paid' and action == 'payment':
                        raise ValidationError('This invoice has already been paid for.')
                    if inv.voided and action not in ['refund','unmatched_refund']:
                        raise ValidationError('You cannot make a payment for an invoice that has been voided.')
                    if (decimal.Decimal(total) > inv.balance) and action == 'payment':
                        raise ValidationError('The amount to be charged is more than the amount payable for this invoice.')

            txn = self._submit_info(order_number,reference,total,action,_type,sub_type,bankcard,orig_txn_number)
            self.friendly_error_msg(txn)
            
            return txn
        except Exception:
            raise

    def store_token(self, user,token,masked_card,expiry_date,card_type):
        token,created = BpointToken.objects.get_or_create(
            user=user,
            DVToken=token,
            masked_card=masked_card,
            expiry_date=datetime.datetime.strptime(expiry_date, '%m%y').date(),
            card_type=card_type
        )
        return token

    def create_token(self,user,reference,bankcard=None,store_card=False):
        ''' Create a token on checkout
            Used to create a token and store it against a
            user when checking out
        '''
        resp =  self.request_token(reference,bankcard)
        if store_card:
            try:
                self.store_token(
                    user,
                    resp.dvtoken,
                    bankcard.obfuscated_number,
                    resp.card_details.expiry_date,
                    resp.card_type
                )
            except IntegrityError as e:
                if 'unique constraint' in e.message:
                    pass
            return '{}|{}|{}'.format(resp.dvtoken,resp.card_details.expiry_date,bankcard.obfuscated_number[-4:])
        else:
            return '{}|{}|{}'.format(resp.dvtoken,resp.card_details.expiry_date,bankcard.obfuscated_number[-4:])

    def pay_with_storedtoken(self,action,_type,sub_type,token_id,order_number=None,reference=None,total=None,orig_txn_number=None):
        ''' Make a payment using a stored card
        '''
        try:
            token = BpointToken.objects.get(id=token_id)
            token.bankcard.last_digits = token.last_digits
            return self.post_transaction(action,_type,sub_type,order_number,reference,total,token.bankcard,orig_txn_number)
        except BpointToken.DoesNotExist as e:
            raise UnableToTakePayment(str(e))

    def pay_with_temptoken(self,action,_type,sub_type,token,order_number=None,reference=None,total=None,orig_txn_number=None,replay=False):
        ''' Make a payment using a temp token
        '''
        try:
            return self.post_transaction(action,_type,sub_type,order_number,reference,total,token,orig_txn_number,replay=replay)
        except BpointToken.DoesNotExist as e:
            raise UnableToTakePayment(str(e))

    def delete_token(self,token):
        try:
            res = self.gateway.delete_token(token)
        except Exception:
            raise
        # Check if the transaction was successful
        if not res.api_response.response_code == 0:
            raise UnableToTakePayment(res.api_response.response_text)
        return res

    def friendly_error_msg(self, txn):
        if not txn.approved:
            if txn.response_code == 'PT_T7':
                raise UnableToTakePayment('Your stored card has expired. Please consider adding a new card and removing this one.')
            else:
                raise UnableToTakePayment(txn.response_txt)
        return False
    
