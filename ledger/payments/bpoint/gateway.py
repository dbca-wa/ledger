import logging
from . import settings
logger = logging.getLogger('bpoint_dpaw')
from ledger.payments.bpoint.BPOINT.API import (TransactionRequest,
                                               Credentials,
                                               TransactionSearchRequest,
                                               AddDVTokenRequest,
                                               DeleteDVTokenRequest)

class Gateway(object):

    def __init__(self,username,password,merchant_number,currency, biller_code, is_test,ois_id):
        self.credentials = Credentials(username,password,str(merchant_number),currency, biller_code, is_test, ois_id)

    def _transaction(self,order_num,reference,action,amount,card_details,biller_code,_type,sub_type):
        '''Perform a transaction with BPOINT.
            @param action: to determine the transaction action in BPOINT
            @param amount: amount of the order
            @param card_details: card to charge for the transaction
            @biller_code: your bpoint biller code
            @param test: used to set the transaction as a test transaction
            so that it cannot be processed bpoint
        '''
        print ("TRANSACTION - _transaction")
        print (self.credentials.biller_code)
        print (self.credentials.is_test)
        print (self.credentials.currency)
        print (self.credentials.merchant_number)
        print (self.credentials.username)
        print (self.credentials.password)

        req = None
        try:
            req = TransactionRequest(credentials=self.credentials)
            req.action=action
            req.biller_code=self.credentials.biller_code
            req.test_mode=self.credentials.is_test
            req.amount=amount
            req.card_details=card_details
            req.currency=self.credentials.currency
            req.type=_type
            req.crn1 = reference
            req.sub_type = sub_type
            req.tokenisation_mode = 3
            req.store_card = True #Store card tokens in order to make refunds
        except Exception as e:
            raise
        return req

    def get_txn_settlement_date(self,settlement_date):
        '''
            Get a specific transaction from BPOINT
        '''
        txn = TransactionSearchRequest(self.credentials)
        txn.settlement_date = settlement_date

        return txn.submit()

    def get_txns_settlement_date(self):
        '''
            Get all transactions from BPOINT
        '''
        return TransactionSearchRequest(self.credentials).submit()


    def get_txn(self,txn_number):
        '''
            Get a specific transaction from BPOINT
        '''
        txn = TransactionSearchRequest(self.credentials)
        txn.txn_number = txn_number
        
        return txn.submit()

    def get_txns(self):
        '''
            Get all transactions from BPOINT
        '''
        return TransactionSearchRequest(self.credentials).submit()

    def request_new_token(self, card, reference):
        req = AddDVTokenRequest(self.credentials)
        req.card_details = card
        req.crn1 = reference
        return req.submit()

    def handle_txn(self,order_num,reference,action,amount,card_details,biller_code,_type,sub_type,orig_txn_num=None):
        '''
            Handle the transaction and pass it
            back to the BPOINT API
        '''
        logger.info('Submitting BPOINT transaction for order {} ({}, {}, ${})'.format(order_num, reference, action, amount))
        txn = self._transaction(order_num,reference,action,amount,card_details,biller_code,_type,sub_type)
        if orig_txn_num:
            txn.original_txn_number = orig_txn_num
        
        return txn.submit()
    
    def delete_token(self,token):
        req = DeleteDVTokenRequest(self.credentials,token)
        return req.submit()
    
    
