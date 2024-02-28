import requests
import datetime
import traceback
import json
import csv
from six.moves import StringIO
from wsgiref.util import FileWrapper
from decimal import Decimal as D
from django.core.mail import EmailMessage
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.urlresolvers import resolve
from six.moves.urllib.parse import urlparse
#
from ledger.payments.models import OracleParser, OracleParserInvoice, Invoice, OracleInterface, OracleInterfaceSystem, OracleInterfacePermission, BpointTransaction, BpayTransaction, OracleAccountCode, OracleOpenPeriod, OracleInterfaceDeduction, OracleInterfaceSystem, LinkedInvoiceGroupIncrementer, LinkedInvoice
#from ledger.payments.invoice import utils
#from oscar.apps.order.models import Order
from ledger.order.models import Order
from ledger.basket.models import Basket
from ledger.order import models as order_model
from ledger.payments.cash.models import CashTransaction
from ledger.payments.bpoint.models import BpointTransaction
from oscar.core.loading import get_class
from confy import env
from decimal import Decimal
from django.db.models import Q
from django.db.models import Count
import logging
logger = logging.getLogger(__name__)


OrderPlacementMixin = get_class('checkout.mixins','OrderPlacementMixin')

def isLedgerURL(url):
    ''' Check if the url is a ledger url
    :return: Boolean
    '''
    match = None
    try:
        match = resolve(urlparse(url)[2])
    except:
        pass
    if match:
        return True
    return False

def checkURL(url):
    try:
        resp = requests.get(url, verify=False)
        resp.raise_for_status()
    except:
        raise

def systemid_check(system):
    system = system[1:]
    if len(system) == 3:
        system = '0{}'.format(system)
    elif len(system) > 4:
        system = system[:4]
    return system


#Oracle Parser
def generateOracleParserFile(oracle_codes):
    strIO = StringIO()
    fieldnames = ['Activity Code','Amount']
    writer = csv.writer(strIO)
    writer.writerow(fieldnames)
    for k,v in oracle_codes.items():
        if v != 0:
            writer.writerow([k,v])
    strIO.flush()
    strIO.seek(0)
    return strIO

def sendInterfaceParserEmail(trans_date,oracle_codes,system_name,system_id,error_email=False,error_string=None):
    try:
        try:
            sys = OracleInterfaceSystem.objects.get(system_id=system_id)
            recipients = sys.recipients.all()
        except OracleInterfaceSystem.DoesNotExist:
            recipients = []
        email_instance = env('EMAIL_INSTANCE','DEV')
        if not error_email:
            dt = datetime.datetime.strptime(trans_date,'%Y-%m-%d').strftime('%d/%m/%Y')
            _file = generateOracleParserFile(oracle_codes)
            email = EmailMessage(
                'Oracle Interface for {} for transactions received on {}'.format(system_name,dt),
                'Oracle Interface Summary File for {} for transactions received on {}'.format(system_name,dt),
                settings.EMAIL_FROM,
                to=[r.email for r in recipients]if recipients else [settings.NOTIFICATION_EMAIL],
                headers={'System-Environment': email_instance}
            )
            email.attach('OracleInterface_{}.csv'.format(dt), _file.getvalue(), 'text/csv')
        else:
            dt = datetime.datetime.strptime(trans_date,'%Y-%m-%d').strftime('%d/%m/%Y')
            today = datetime.datetime.now().strftime('%d/%m/%Y')
            subject = 'Oracle Interface Error for {} for transactions received on {}'.format(system_name,dt)
            email = EmailMessage(subject,
                'There was an error in generating a summary report for the oracle interface parser for transactions processed on {}.Please refer to the following log output:\n\n\n{}'.format(today,error_string),
                settings.EMAIL_FROM,
                to=[r.email for r in recipients]if recipients else [settings.NOTIFICATION_EMAIL],
                headers={'System-Environment': email_instance}
            )

        email.send()
    except Exception as e:
        print(traceback.print_exc())
        raise e

def addToInterface(date,oracle_codes,system,override):
    try:
        dt = datetime.datetime.strptime(date,'%Y-%m-%d')
        trans_date = datetime.datetime.strptime(date,'%Y-%m-%d')#.strftime('%d/%m/%Y')
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        oracle_date = '{}-{}'.format(dt.strftime('%B').upper(),dt.strftime('%y'))
        if not override:
            try:
                OracleOpenPeriod.objects.get(period_name=oracle_date)
            except OracleOpenPeriod.DoesNotExist:
                raise ValidationError('There is currently no open period for transactions done on {}'.format(trans_date))

        # create dictionary of OracleInterface records for line items in transaction
        records = {}
        for k, v in oracle_codes.items():
            if k not in records:
                records[k] = OracleInterface.objects.create(
                    receipt_date = trans_date,
                    activity_name = k,
                    amount = D(v),
                    customer_name = system.system_name,
                    description = k,
                    source = system.source,
                    method = system.method,
                    comments = '{} GST/{}'.format(k,date),
                    status = 'NEW',
                    status_date = today
                )

        deductions_only = set()

        # add empty stubs for deductions
        for k, v in oracle_codes.items():
            deduction_qs = OracleInterfaceDeduction.objects.filter(oisystem=system, percentage_account_code=k)
            if deduction_qs and system.deduct_percentage:
                for deduction in deduction_qs:
                    if (not deduction.percentage or not deduction.destination_account_code):
                        raise Exception('Deduction Percentage and an oracle account are required if deduction is enabled.')

                    try:
                        OracleAccountCode.objects.filter(active_receivables_activities=deduction.destination_account_code)
                    except OracleAccountCode.DoesNotExist:
                        raise ValidationError('The account code setup for oracle deduction does not exist.')

                    if deduction.destination_account_code not in records:
                        records[deduction.destination_account_code] = OracleInterface.objects.create(
                            receipt_date = trans_date,
                            activity_name = deduction.destination_account_code,
                            amount = D(0),
                            customer_name = system.system_name,
                            description = deduction.destination_account_code,
                            source = system.source,
                            method = system.method,
                            comments = '{} GST/{}'.format(deduction.destination_account_code,date),
                            status = 'NEW',
                            status_date = today
                        )
                        deductions_only.add(deduction.destination_account_code)

        for k,v in oracle_codes.items():
            if v != 0:
                found = OracleAccountCode.objects.filter(active_receivables_activities=k)
                if not found:
                    raise ValidationError('{} is not a valid account code'.format(k))

                # Check if there is a deduction for that system/account code, and sends to another oracle account code
                deduction_qs = OracleInterfaceDeduction.objects.filter(oisystem=system, percentage_account_code=k)

                if deduction_qs and system.deduct_percentage:

                    # sanity check: deductions should not transfer money to an account code that shows up as a line item
                    if k in deductions_only:
                        raise ValidationError('A deduction cannot transfer money to a line item that is also being deducted from')

                    initial_amount = D(v)
                    remainder_amount = initial_amount

                    for deduction in deduction_qs:

                        # Add the deducted amount to the oracle code specified in the system table
                        deduction_amount = deduction.percentage * initial_amount / D(100)
                        records[deduction.destination_account_code].amount += deduction_amount
                        remainder_amount -= deduction_amount

                    records[k].amount = remainder_amount

        # save records
        for record in records.values():
            record.save()

        return {k: v.amount for k, v in records.items()}
    except:
        raise


def oracle_parser(date,system,system_name,override=False):
    invoices = []
    invoice_list = []
    oracle_codes = {}
    parser_codes = {}
    try:
        try:
            ois = OracleInterfaceSystem.objects.get(system_id=system)
        except OracleInterfaceSystem.DoesNotExist:
            raise Exception('No system with id {} exists for integration with oracle'.format(system))
        if not ois.enabled:
            raise Exception('The oracle job is not enabled for {}'.format(ois.system_name))
        with transaction.atomic():
            op,created = OracleParser.objects.get_or_create(date_parsed=date)
            bpoint_txns = []
            bpay_txns = []
            bpoint_txns.extend([x for x in BpointTransaction.objects.filter(settlement_date=date,response_code=0).exclude(crn1__endswith='_test')])
            bpay_txns.extend([x for x in BpayTransaction.objects.filter(p_date__contains=date, service_code=0)])
            # Get the required invoices
            for b in bpoint_txns:
                if b.crn1 not in invoice_list:
                    invoice = Invoice.objects.get(reference=b.crn1)
                    if invoice.system == system:
                        invoices.append(invoice)
                        invoice_list.append(b.crn1)
            for b in bpay_txns:
                if b.crn not in invoice_list:
                    invoice = Invoice.objects.get(reference=b.crn)
                    if invoice.system == system:
                        invoices.append(invoice)
                        invoice_list.append(b.crn)
            for invoice in invoices:
                if invoice.order:
                    if invoice.reference not in parser_codes.keys():
                        parser_codes[invoice.reference] = {}
                    # Go through the items
                    items = invoice.order.lines.all()
                    items_codes = [{'id':i.id,'code':i.oracle_code} for i in items]
                    for i in items_codes:
                        v = i['code']
                        k = i['id']
                        if i['code'] not in oracle_codes.keys():
                            oracle_codes[v] = D('0.0')
                        if i['id'] not in parser_codes[invoice.reference].keys():
                            parser_codes[invoice.reference].update({k:{'code':v,'payment': D('0.0'),'refund': D('0.0'),'deductions': D('0.0')}})

                    # Start passing items in the invoice
                    for i in items:
                        code = i.oracle_code
                        item_id = i.id
                        # Check previous parser results for this invoice
                        previous_invoices = OracleParserInvoice.objects.filter(reference=invoice.reference,parser__date_parsed=date)
                        code_paid_amount = D('0.0')
                        code_refunded_amount = D('0.0')
                        code_deducted_amount = D('0.0')
                        for p in previous_invoices:
                            details = dict(json.loads(p.details))
                            for k,v in details.items():
                                p_item = details[k]
                                if int(k) == item_id:
                                    code_paid_amount +=  D(p_item['payment'])
                                    code_refunded_amount += D(p_item['refund'])
                                    code_deducted_amount += D(p_item['deductions'])
                        # Deal with the current item
                        # Payments
                        paid_amount = D('0.0')
                        for k,v in i.payment_details['bpay'].items():
                            b_txn = BpayTransaction.objects.get(id=k)
                            paid_amount += D(v) if b_txn.p_date.strftime('%Y-%m-%d') == date else D(0.0)
                        for k,v in i.payment_details['card'].items():
                            b_txn = BpointTransaction.objects.get(id=k)
                            paid_amount += D(v) if str(b_txn.settlement_date) == date else D(0.0)
                        code_payable_amount = paid_amount - code_paid_amount
                        if code_payable_amount >= 0:
                            oracle_codes[code] += code_payable_amount
                            for k,v in parser_codes[invoice.reference][item_id].items():
                                item = parser_codes[invoice.reference][item_id]
                                if k == 'payment':
                                    item[k] += code_payable_amount

                        # Deductions
                        deducted_amount = D('0.0')
                        for k,v in i.deduction_details['cash'].items():
                            c_txn = CashTransaction.objects.get(id=k)
                            deducted_amount += D(v) if c_txn.created.strftime('%Y-%m-%d') == date else D(0.0)
                        code_deductable_amount = deducted_amount - code_deducted_amount
                        if code_deductable_amount >= 0:
                            oracle_codes[code] -= code_deductable_amount
                            for k,v in parser_codes[invoice.reference][item_id].items():
                                item = parser_codes[invoice.reference][item_id]
                                if k == 'deductions':
                                    item[k] += code_deductable_amount

                        # Refunds
                        refunded_amount = D('0.0')
                        for k,v in i.refund_details['bpay'].items():
                            b_txn = BpayTransaction.objects.get(id=k)
                            refunded_amount += D(v) if b_txn.p_date.strftime('%Y-%m-%d') == date else D(0.0)
                        for k,v in i.refund_details['card'].items():
                            b_txn = BpointTransaction.objects.get(id=k)
                            refunded_amount += D(v) if str(b_txn.settlement_date) == date else D(0.0)
                        code_refundable_amount = refunded_amount - code_refunded_amount
                        if code_refundable_amount >= 0:
                            oracle_codes[code] -= code_refundable_amount
                            for k,v in parser_codes[invoice.reference][item_id].items():
                                item = parser_codes[invoice.reference][item_id]
                                if k == 'refund':
                                    item[k] += code_refundable_amount

            # Convert Deimals to strings as they cannot be serialized
            for k,v in parser_codes.items():
                for a,b in v.items():
                    for r,f in b.items():
                        parser_codes[k][a][r] = str(parser_codes[k][a][r])
            for k,v in parser_codes.items():
                can_add = False
                for g,h in v.items():
                    if h['payment'] != 0 or h['refund'] != 0 or h['deductions'] != 0:
                        can_add = True
                if can_add:
                    OracleParserInvoice.objects.create(reference=k,details=json.dumps(v),parser=op)
            # Add items to oracle interface table
            new_codes = addToInterface(date,oracle_codes,ois,override)
            # Send an email with all the activity codes entered into the interface table
            sendInterfaceParserEmail(date,new_codes,system_name,system)
            return oracle_codes
    except Exception as e:
        error = traceback.format_exc()
        sendInterfaceParserEmail(date,oracle_codes,system_name,system,error_email=True,error_string=error)
        raise e

def oracle_parser_on_invoice(date,system,system_name,override=False):
    '''Oracle parse uses invoices to build a total of allocated payments, refund and money that needs to be rellocated to alternative oracle codes.'''

    invoices = []
    invoice_list = []
    oracle_codes = {}
    parser_codes = {}
    oracle_parser_invoices = []
    try:
        try:
            ois = OracleInterfaceSystem.objects.get(system_id=system)
        except OracleInterfaceSystem.DoesNotExist:
            raise Exception('No system with id {} exists for integration with oracle'.format(system))
        if not ois.enabled:
            raise Exception('The oracle job is not enabled for {}'.format(ois.system_name))
        with transaction.atomic():
            op,created = OracleParser.objects.get_or_create(date_parsed=date)
            op_invoices = OracleParserInvoice.objects.filter(parser=op)

            #Build a list of invoices already in the oracle parse for parse date query
            for opi in op_invoices:
               oracle_parser_invoices.append(opi.reference)
            invoices = Invoice.objects.filter(settlement_date=date, system=system)

            #Loop through invoices
            for invoice in invoices:
                # If invoice already exists in the parse date than skip and move to next invoice.
                if invoice.reference in oracle_parser_invoices:
                     continue

                if invoice.order:
                    if invoice.reference not in parser_codes.keys():
                        parser_codes[invoice.reference] = {}
                    # Go through the items
                    items = invoice.order.lines.all()
                    items_codes = [{'id':i.id,'code':i.oracle_code} for i in items]
                    for i in items_codes:
                        v = i['code']
                        k = i['id']
                        if i['code'] not in oracle_codes.keys():
                            oracle_codes[v] = D('0.0')
                        if i['id'] not in parser_codes[invoice.reference].keys():
                            parser_codes[invoice.reference].update({k:{'code':v, 'payment': D('0.0'),'refund': D('0.0'),'deductions': D('0.0'), 'order': D('0.0')}})

                    # Start passing items in the invoice
                    for i in items:
                        code = i.oracle_code
                        item_id = i.id
                        # Check previous parser results for this invoice
                        previous_invoices = OracleParserInvoice.objects.filter(reference=invoice.reference,parser__date_parsed=date)
                        code_paid_amount = D('0.0')
                        code_refunded_amount = D('0.0')
                        code_deducted_amount = D('0.0')
                        for p in previous_invoices:
                            details = dict(json.loads(p.details))
                            for k,v in details.items():
                                p_item = details[k]
                                if int(k) == item_id:
                                    code_paid_amount +=  D(p_item['payment'])
                                    code_refunded_amount += D(p_item['refund'])
                                    code_deducted_amount += D(p_item['deductions'])
                        # Deal with the current item
                        # Payments
                        paid_amount = D('0.0')
                        for k,v in i.payment_details['bpay'].items():
                            b_txn = BpayTransaction.objects.get(id=k)
                            paid_amount += D(v) if b_txn.p_date.strftime('%Y-%m-%d') == date else D(0.0)
                        for k,v in i.payment_details['card'].items():
                            b_txn = BpointTransaction.objects.get(id=k)
                            paid_amount += D(v) if str(b_txn.settlement_date) == date else D(0.0)
                        code_payable_amount = paid_amount - code_paid_amount
                        if code_payable_amount >= 0:
                            oracle_codes[code] += code_payable_amount
                            for k,v in parser_codes[invoice.reference][item_id].items():
                                item = parser_codes[invoice.reference][item_id]
                                if k == 'payment':
                                    item[k] += code_payable_amount
                        # Deductions
                        deducted_amount = D('0.0')
                        for k,v in i.deduction_details['cash'].items():
                            c_txn = CashTransaction.objects.get(id=k)
                            deducted_amount += D(v) if c_txn.created.strftime('%Y-%m-%d') == date else D(0.0)
                        code_deductable_amount = deducted_amount - code_deducted_amount
                        #if code_deductable_amount >= 0:
                        oracle_codes[code] -= code_deductable_amount
                        for k,v in parser_codes[invoice.reference][item_id].items():
                            item = parser_codes[invoice.reference][item_id]
                            if k == 'deductions':
                                item[k] += code_deductable_amount

                        # Refunds
                        refunded_amount = D('0.0')
                        for k,v in i.refund_details['bpay'].items():
                            b_txn = BpayTransaction.objects.get(id=k)
                            refunded_amount += D(v) if b_txn.p_date.strftime('%Y-%m-%d') == date else D(0.0)
                        for k,v in i.refund_details['card'].items():
                            b_txn = BpointTransaction.objects.get(id=k)
                            refunded_amount += D(v) if str(b_txn.settlement_date) == date else D(0.0)
                        code_refundable_amount = refunded_amount - code_refunded_amount
                        if code_refundable_amount >= 0:
                            oracle_codes[code] -= code_refundable_amount
                            for k,v in parser_codes[invoice.reference][item_id].items():
                                item = parser_codes[invoice.reference][item_id]
                                if k == 'refund':
                                    item[k] += code_refundable_amount

                        # Order Calculations
                        if 'order' in i.payment_details:
                             order_amount = D('0.0')
                             for k,v in i.payment_details['order'].items():
                                 #c_txn = CashTransaction.objects.get(id=k)
                                 deducted_amount += D(v) #if c_txn.created.strftime('%Y-%m-%d') == date else D(0.0)
                             code_deductable_amount = deducted_amount - code_deducted_amount
                             #if code_deductable_amount >= 0:
                             oracle_codes[code] += code_deductable_amount
                             for k,v in parser_codes[invoice.reference][item_id].items():
                                 item = parser_codes[invoice.reference][item_id]
                                 if k == 'order':
                                     item[k] += code_deductable_amount
            # Convert Deimals to strings as they cannot be serialized
            for k,v in parser_codes.items():
                for a,b in v.items():
                    for r,f in b.items():
                        parser_codes[k][a][r] = str(parser_codes[k][a][r])
            for k,v in parser_codes.items():
                can_add = False
                if k not in oracle_parser_invoices:
                    can_add = True
                if can_add:
                    OracleParserInvoice.objects.create(reference=k,details=json.dumps(v),parser=op)
            # Add items to oracle interface table
            new_codes = addToInterface(date,oracle_codes,ois,override)
            # Send an email with all the activity codes entered into the interface table
            sendInterfaceParserEmail(date,new_codes,system_name,system)
            return oracle_codes
    except Exception as e:
        error = traceback.format_exc()
        sendInterfaceParserEmail(date,oracle_codes,system_name,system,error_email=True,error_string=error)
        raise e


def update_payments(invoice_reference):
    UPDATE_PAYMENT_ALLOCATION = env('UPDATE_PAYMENT_ALLOCATION', False)

    system_id = invoice_reference[:4]
    ois = OracleInterfaceSystem.objects.filter(system_id=system_id)
    if ois.count() > 0:
         if ois[0].integration_type == 'bpoint_api':
             if ois[0].oracle_calculation == 'version_2':
                     UPDATE_PAYMENT_ALLOCATION = True             


    if UPDATE_PAYMENT_ALLOCATION is True:
        # New functionality to assign payments to relevant line items ensuring payments, refunds and booking changes are allocated to the correct oracle codes.
        update_payments_allocation(invoice_reference)
    else:
        with transaction.atomic():
            try:
                i = None
                try:
                    i = Invoice.objects.get(reference=str(invoice_reference))
                except Invoice.DoesNotExist:
                    raise ValidationError('The invoice with refererence {} does not exist'.format(invoice_reference))
                refunded = D(0.0)
                paid = D(0.0)
                deductions = D(0.0)
                # Bpoint Transactions
                if i.order:
                    for line in i.order.lines.all():
                        paid_amount = line.paid
                        refunded_amount = line.refunded
                        deducted_amount = line.deducted
                        amount = line.line_price_incl_tax
                        total_paid = i.total_payment_amount
                        total_refund = i.refund_amount
                        total_deductions = i.deduction_amount
                        paid += paid_amount
                        refunded += refunded_amount
                        deductions += deducted_amount
                        # Bpoint Amounts
                        for bpoint in i.bpoint_transactions:
                            if bpoint.approved:
                                if paid_amount < amount and paid < total_paid:
                                    if bpoint.action == 'payment':
                                        remaining_amount = amount - paid_amount
                                        remaining_payable_amount = total_paid - paid
                                        unallocated = bpoint.amount - bpoint.payment_allocated
                                        if str(bpoint.id) in line.payment_details['card'].keys() and remaining_payable_amount > 0:
                                            if remaining_amount <= unallocated:
                                                new_amount = D(line.payment_details['card'][str(bpoint.id)]) + remaining_amount
                                            else:
                                                new_amount = D(line.payment_details['card'][str(bpoint.id)]) + unallocated
                                            if unallocated > 0:
                                                line.payment_details['card'][str(bpoint.id)] = str(new_amount)
                                                paid_amount += new_amount
                                                paid += new_amount
                                        else:
                                            if remaining_amount <= unallocated:
                                                new_amount = D(0.0) + remaining_amount
                                            else:
                                                new_amount = D(0.0) + unallocated
                                            line.payment_details['card'][bpoint.id] = str(new_amount)
                                            paid_amount += new_amount
                                            paid += new_amount
                                if refunded_amount < amount and refunded < total_refund:
                                    if bpoint.action == 'refund':
                                        remaining_amount = amount - refunded_amount
                                        remaining_refundable_amount = total_refund - refunded
                                        unallocated = bpoint.amount - bpoint.refund_allocated
                                        if str(bpoint.id) in line.refund_details['card'].keys() and remaining_refundable_amount > 0:
                                            if remaining_amount <= unallocated:
                                                new_amount = D(line.refund_details['card'][str(bpoint.id)]) + remaining_amount
                                            else:
                                                new_amount = D(line.refund_details['card'][str(bpoint.id)]) + unallocated
                                            if unallocated > 0:
                                                line.refund_details['card'][str(bpoint.id)] = str(new_amount)
                                                refunded_amount += new_amount
                                                refunded += new_amount
                                        else:
                                            if remaining_amount <= unallocated:
                                                new_amount = D(0.0) + remaining_amount
                                            else:
                                                new_amount = D(0.0) + unallocated
                                            line.refund_details['card'][bpoint.id] = str(new_amount)
                                            refunded_amount += new_amount
                                            refunded += new_amount
                        # Bpay Transactions
                        for bpay in i.bpay_transactions:
                            if bpay.approved:
                                if paid_amount < amount and paid < total_paid:
                                    if bpay.p_instruction_code == '05' and bpay.type == '399':
                                        remaining_amount = amount - paid_amount
                                        remaining_payable_amount = total_paid - paid
                                        unallocated = bpay.amount - bpay.payment_allocated
                                        if str(bpay.id) in line.payment_details['bpay'].keys() and remaining_payable_amount > 0:
                                            if remaining_amount <= unallocated:
                                                new_amount = D(line.payment_details['bpay'][str(bpay.id)]) + remaining_amount
                                            else:
                                                new_amount = D(line.payment_details['bpay'][str(bpay.id)]) + unallocated
                                            if unallocated > 0:
                                                line.payment_details['bpay'][str(bpay.id)] = str(new_amount)
                                                paid_amount += new_amount
                                                paid += new_amount
                                        else:
                                            if remaining_amount <= unallocated:
                                                new_amount = D(0.0) + remaining_amount
                                            else:
                                                new_amount = D(0.0) + unallocated
                                            line.payment_details['bpay'][bpay.id] = str(new_amount)
                                            paid_amount += new_amount
                                            paid += new_amount
                                if refunded_amount < amount and refunded < total_refund:
                                    if bpay.p_instruction_code == '25' and bpay.type == '699':
                                        remaining_amount = amount - refunded_amount
                                        remaining_refundable_amount = total_refund - refunded
                                        unallocated = bpay.amount - bpay.refund_allocated
                                        if str(bpay.id) in line.refund_details['bpay'].keys() and remaining_refundable_amount > 0:
                                            if remaining_amount <= unallocated:
                                                new_amount = D(line.refund_details['bpay'][str(bpay.id)]) + remaining_amount
                                            else:
                                                new_amount = D(line.refund_details['bpay'][str(bpay.id)]) + unallocated
                                            if unallocated > 0:
                                                line.refund_details['bpay'][str(bpay.id)] = str(new_amount)
                                                refunded_amount += new_amount
                                                refunded += new_amount
                                        else:
                                            if remaining_amount <= unallocated:
                                                new_amount = D(0.0) + remaining_amount
                                            else:
                                                new_amount = D(0.0) + unallocated
                                            line.refund_details['bpay'][bpay.id] = str(new_amount)
                                            refunded_amount += new_amount
                                            refunded += new_amount
                        # Cash Transactions
                        for c in i.cash_transactions.all():
                            if paid_amount < amount and paid < total_paid:
                                if c.type in ['payment','move_in']:
                                    remaining_amount = amount - paid_amount
                                    remaining_payable_amount = total_paid - paid
                                    unallocated = c.amount - c.payment_allocated
                                    if str(c.id) in line.payment_details['cash'].keys() and remaining_payable_amount > 0:
                                        if remaining_amount <= unallocated:
                                            new_amount = D(line.payment_details['cash'][str(c.id)]) + remaining_amount
                                        else:
                                            new_amount = D(line.payment_details['cash'][str(c.id)]) + unallocated
                                        if unallocated > 0:
                                            line.payment_details['cash'][str(c.id)] = str(new_amount)
                                            paid_amount += new_amount
                                            paid += new_amount
                                    else:
                                        if remaining_amount <= unallocated:
                                            new_amount = D(0.0) + remaining_amount
                                        else:
                                            new_amount = D(0.0) + unallocated
                                        line.payment_details['cash'][c.id] = str(new_amount)
                                        paid_amount += new_amount
                                        paid += new_amount
                            if deducted_amount < amount and deductions < total_deductions:
                                if c.type == 'move_out':
                                    remaining_amount = amount - deducted_amount
                                    remaining_deductable_amount = total_deductions - deductions
                                    unallocated = c.amount - c.deduction_allocated
                                    if str(c.id) in line.deduction_details['cash'].keys():
                                        if remaining_amount <= unallocated:
                                            new_amount = D(line.deduction_details['cash'][str(c.id)]) + remaining_amount
                                        else:
                                            new_amount = D(line.deduction_details['cash'][str(c.id)]) + unallocated
                                        if unallocated > 0:
                                            line.deduction_details['cash'][str(c.id)] = str(new_amount)
                                            deducted_amount += new_amount
                                            deductions += new_amount
                                    else:
                                        if remaining_amount <= unallocated:
                                            new_amount = D(0.0) + remaining_amount
                                        else:
                                            new_amount = D(0.0) + unallocated
                                        line.deduction_details['cash'][c.id] = str(new_amount)
                                        deducted_amount += new_amount
                                        deductions += new_amount
                            if refunded_amount < amount and refunded < total_refund:
                                if c.type == 'refund':
                                    remaining_amount = amount - refunded_amount
                                    remaining_refundable_amount = total_refund - refunded
                                    unallocated = c.amount - c.refund_allocated
                                    if str(c.id) in line.refund_details['cash'].keys() and remaining_refundable_amount > 0:
                                        if remaining_amount <= unallocated:
                                            new_amount = D(line.refund_details['cash'][str(c.id)]) + remaining_amount
                                        else:
                                            new_amount = D(line.refund_details['cash'][str(c.id)]) + unallocated
                                        if unallocated > 0:
                                            line.refund_details['cash'][str(c.id)] = str(new_amount)
                                            refunded_amount += new_amount
                                            refunded += new_amount
                                    else:
                                        if remaining_amount <= unallocated:
                                            new_amount = D(0.0) + remaining_amount
                                        else:
                                            new_amount = D(0.0) + unallocated
                                        line.refund_details['cash'][c.id] = str(new_amount)
                                        refunded_amount += new_amount
                                        refunded += new_amount
                        line.save()
                # Check if the whole amount paid on the invoice has been allocated otherwise add to the first line item
                if i.total_payment_amount > paid:
                    first_item = i.order.lines.first()
                    # Bpoint
                    for b in i.bpoint_transactions:
                        if b.payment_allocated < b.amount and b.action == 'payment':
                            if first_item.payment_details['card'].get(str(b.id)):
                                first_item.payment_details['card'][str(b.id)] = str(D(first_item.payment_details['card'][str(b.id)]) + (b.amount - b.payment_allocated))
                            else:
                                first_item.payment_details['card'][str(b.id)] = str(b.amount - b.payment_allocated)
                    # Bpay
                    for b in i.bpay_transactions:
                        if b.payment_allocated < b.amount and b.p_instruction_code == '05' and b.type == '399':
                            if first_item.payment_details['bpay'].get(str(b.id)):
                                first_item.payment_details['bpay'][str(b.id)] = str(D(first_item.payment_details['bpay'][str(b.id)]) + (b.amount - b.payment_allocated))
                            else:
                                first_item.payment_details['bpay'][str(b.id)] = str(b.amount - b.payment_allocated)
                    # Cash
                    for b in i.cash_transactions.all():
                        if b.payment_allocated < b.amount and b.type in ['payment','move_in']:
                            if first_item.payment_details['cash'].get(str(b.id)):
                                first_item.payment_details['cash'][str(b.id)] = str(D(first_item.payment_details['cash'][str(b.id)]) + (b.amount - b.payment_allocated))
                            else:
                                first_item.payment_details['cash'][str(b.id)] = str(b.amount - b.payment_allocated)
                    first_item.save()
                if i.refund_amount > refunded:
                    first_item = i.order.lines.first()
                    # Bpoint
                    for b in i.bpoint_transactions:
                        if b.refund_allocated < b.amount and b.action == 'refund':
                            if first_item.refund_details['card'].get(str(b.id)):
                                first_item.refund_details['card'][str(b.id)] = str(D(first_item.refund_details['card'][str(b.id)]) + (b.amount - b.refund_allocated))
                            else:
                                first_item.refund_details['card'][str(b.id)] = str(b.amount - b.refund_allocated)
                    # Bpay
                    for b in i.bpay_transactions:
                        if b.refund_allocated < b.amount and b.p_instruction_code == '25' and b.type == '699':
                            if first_item.refund_details['bpay'].get(str(b.id)):
                                first_item.refund_details['bpay'][str(b.id)] = str(D(first_item.refund_details['bpay'][str(b.id)]) + (b.amount - b.refund_allocated))
                            else:
                                first_item.refund_details['bpay'][str(b.id)] = str(b.amount - b.refund_allocated)
                    # Cash
                    for b in i.cash_transactions.all():
                        if b.refund_allocated < b.amount and b.type == 'refund':
                            if first_item.refund_details['cash'].get(str(b.id)):
                                first_item.refund_details['cash'][str(b.id)] = str(D(first_item.refund_details['cash'][str(b.id)]) + (b.amount - b.refund_allocated))
                            else:
                                first_item.refund_details['cash'][str(b.id)] = str(b.amount - b.refund_allocated)
                    first_item.save()
            except:
                print(traceback.print_exc())
                raise

def update_payments_allocation(invoice_reference):

    with transaction.atomic():
        try:
            i = None
            try:
                i = Invoice.objects.get(reference=str(invoice_reference))
            except Invoice.DoesNotExist:
                raise ValidationError('The invoice with refererence {} does not exist'.format(invoice_reference))

            refunded = D(0.0)
            paid = D(0.0)
            deductions = D(0.0)
            oracle_code_totals = {}

            invoice_settlement_date = None
            if BpointTransaction.objects.filter(crn1=i.reference).count() > 0:
                bp = BpointTransaction.objects.filter(crn1=i.reference)[0]
                invoice_settlement_date = bp.settlement_date
            else:
                invoice_settlement_date = datetime.datetime.now().date()

            # Get Order Information
            if i.order:
                no_oracle = i.order.basket.no_oracle
                # total amount based on oracle code to get a negiative / positive value.
                for line in i.order.lines.all():
                    if line.oracle_code not in oracle_code_totals:
                            oracle_code_totals[line.oracle_code] = Decimal('0.00')
                    oracle_code_totals[line.oracle_code] = oracle_code_totals[line.oracle_code] + line.line_price_incl_tax

                # assign payment or refund based on oracle code
                for line in i.order.lines.all():
                    paid_amount = line.paid
                    refunded_amount = line.refunded
                    deducted_amount = line.deducted
                    amount = line.line_price_incl_tax
                    total_paid = i.total_payment_amount
                    total_refund = i.refund_amount
                    total_deductions = i.deduction_amount
                    line_status = line.line_status
                    paid += paid_amount
                    refunded += refunded_amount
                    deductions += deducted_amount
                    if line:
                        if line.id:
                              line.deduction_details['cash'] = {}
                              line.refund_details['cash'] = {}
                              line.payment_details['cash'] = {}

                              line.refund_details['order'] = {}
                              line.payment_details['order']  = {}
                              line.deduction_details['order']  = {}
                              if no_oracle is True:
                                  pass
                              else:
                                  if line is not None:
                                     # look for lines under invoice --> order that are new line
                                     if line.line_price_incl_tax > 0 and line.line_status == 1:
                                             if oracle_code_totals[line.oracle_code] >= line.line_price_incl_tax:
                                                 line.payment_details['order'][str(line.id)] = str(line.line_price_incl_tax)
                                                 oracle_code_totals[line.oracle_code] = oracle_code_totals[line.oracle_code] - line.line_price_incl_tax
                                     # look for lines under invoice --> order that are have been removed
                                     if line.line_price_incl_tax < 0 and line.line_status == 3:
                                             line.payment_details['order'][str(line.id)] = str(oracle_code_totals[line.oracle_code])
                                             oracle_code_totals[line.oracle_code] =  oracle_code_totals[line.oracle_code] - oracle_code_totals[line.oracle_code]


                    line.save()
                if i.settlement_date is None:
                   i.settlement_date = invoice_settlement_date
                   i.save()
        except:
            print(traceback.print_exc())
            raise


def bpoint_integrity_checks(system,days,rowlimit):
    rows = []
    if rowlimit is None:
        rowlimit = 10
    if days is None:
        days = 5
    fromdays = datetime.datetime.today() - datetime.timedelta(days=days)
    # delay check after a recent payment
    from_minute = datetime.datetime.now() - datetime.timedelta(seconds=70)    

    bt = BpointTransaction.objects.filter(crn1__istartswith=system, integrity_check=False, created__gt=fromdays, created__lt=from_minute).order_by('-id')[:rowlimit]
    for b in bt:
        i = Invoice.objects.filter(reference=b.crn1)
        if i.count() > 0:
            o = Order.objects.filter(number=i[0].order_number)
            if o.count() > 0:
                if o[0].basket:
                    if o[0].basket.booking_reference is not None:
                        if len(o[0].basket.booking_reference) > 0:
                             rows.append({'bpoint_id': b.id ,'reference': b.crn1, 'order_number': i[0].order_number, 'basket': o[0].basket.id, 'booking_reference': o[0].basket.booking_reference})

    return rows

def bpoint_integrity_checks_completed(bpoint_id,crn1):
    try:  
       bpt = BpointTransaction.objects.filter(id=bpoint_id,crn1=crn1)
       if bpt.count() > 0:
           for b in bpt:
               b.integrity_check = True
               b.save()
               return True
       return False
    except:
        return False



def LinkedInvoiceCreate(invoice, basket_id):
        print ("CREATING INVOICE LINK")
        basket = Basket.objects.get(id=basket_id)
        system_id = basket.system.replace("S","0")
        ois = OracleInterfaceSystem.objects.get(system_id=system_id)
        li = None
        lig = None
    
        if basket.booking_reference: 
             if len(basket.booking_reference) > 0:
                  if LinkedInvoice.objects.filter(invoice_reference=invoice.reference,system_identifier=ois,booking_reference=basket.booking_reference, booking_reference_linked=basket.booking_reference_link).count():
                      print ("LinkedInvoice already exists, not dupilication")
                  else:
                      if basket.booking_reference_link:
                            if len(basket.booking_reference_link) > 0:
                                li = LinkedInvoice.objects.filter(system_identifier=ois,booking_reference=basket.booking_reference_link)
                                if li.count() > 0:
                                    lig = li[0].invoice_group_id                                  
                                else:
                                    libr = LinkedInvoice.objects.filter(system_identifier=ois,booking_reference=basket.booking_reference)
                                    if libr.count() > 0:
                                        lig = libr[0].invoice_group_id

                      if lig is None:
                            if len(basket.booking_reference) > 0:
                                libr = LinkedInvoice.objects.filter(system_identifier=ois,booking_reference=basket.booking_reference)
                                if libr.count() > 0:
                                    lig = libr[0].invoice_group_id
                            
                      if lig is None:
                           lig = LinkedInvoiceGroupIncrementer.objects.create(system_identifier=ois)
                      booking_reference_linked = basket.booking_reference_link
                      if booking_reference_linked is None:
                           booking_reference_linked = basket.booking_reference
                      if len(booking_reference_linked) > 0:
                          pass
                      else:
                          booking_reference_linked = basket.booking_reference

                            
                      lininv = LinkedInvoice.objects.create(invoice_reference=invoice.reference, system_identifier=ois,booking_reference=basket.booking_reference,booking_reference_linked=booking_reference_linked, invoice_group_id=lig)


#def allocate_refund_to_invoice(request, booking_reference, lines, invoice_text=None, internal=False, order_total='0.00',user=None):
#        basket_params = {
#            'products': lines,
#            'vouchers': [],
#            'system': settings.PS_PAYMENT_SYSTEM_ID,
#            'custom_basket': True,
#            'booking_reference': booking_reference
#        }
#        basket, basket_hash = create_basket_session(request, basket_params)
#        ci = utils.CreateInvoiceBasket()
#        order  = ci.create_invoice_and_order(basket, total=None, shipping_method='No shipping required',shipping_charge=False, user=user, status='Submitted', invoice_text='Oracle Allocation Pools', )
#        new_invoice = Invoice.objects.get(order_number=order.number)
#        update_payments(new_invoice.reference)
#        return order
#

def ledger_payment_invoice_calulations(invoice_group_id, invoice_no, booking_reference, receipt_no, txn_number):
        if invoice_no is None:
            invoice_no = ''
        if booking_reference is None:
            booking_reference =''
        if receipt_no is None:
            receipt_no = ''
        if txn_number is None:
            txn_number = ''
    
        data = {"status": 403, "data": {}} 
        exists=False
        if len(invoice_no) > 0:
            link_res = LinkedInvoice.objects.filter(invoice_reference=invoice_no)
            if link_res.count() > 0:
                invoice_group_id = link_res[0].invoice_group_id.id
        elif len(receipt_no) > 0:
            bt = BpointTransaction.objects.filter(receipt_number=receipt_no)
            crn1=None
            if bt.count() > 0:
                 crn1 = bt[0].crn1
                 link_res = LinkedInvoice.objects.filter(invoice_reference=crn1)
                 if link_res.count() > 0:
                     invoice_group_id = link_res[0].invoice_group_id.id
        elif len(txn_number) > 0:
            bt = BpointTransaction.objects.filter(txn_number=txn_number)
            crn1=None
            if bt.count() > 0:
                 crn1 = bt[0].crn1
                 link_res = LinkedInvoice.objects.filter(invoice_reference=crn1)
                 if link_res.count() > 0:
                     invoice_group_id = link_res[0].invoice_group_id.id
        elif len(booking_reference) > 0:
            link_res = LinkedInvoice.objects.filter(booking_reference=booking_reference)
            if link_res.count() > 0:
                invoice_group_id = link_res[0].invoice_group_id.id

        if invoice_group_id:
                if int(invoice_group_id) > 0:
                     linkinv = LinkedInvoice.objects.filter(invoice_group_id=invoice_group_id)                     
                     system_id = None
                     if linkinv.count() > 0:
                         system_id = linkinv[0].system_identifier.system_id
                         latest_li = LinkedInvoice.objects.filter(invoice_group_id=invoice_group_id).order_by('-created')[0]
                         linked_payments = []
                         linked_payments_booking_references = []
                         invoices = []
                         invoices_data = []
                         orders = []
                         invoice_group_checks_total = 0
                         for li in linkinv:                             
                             invoices.append(li.invoice_reference)
                             inv = Invoice.objects.filter(reference=li.invoice_reference)
                             settlement_date = ''
                             oracle_invoice_number = ''
                             if inv.count() > 0:
                                 settlement_date = inv[0].settlement_date.strftime("%d/%m/%Y")
                                 oracle_invoice_number = inv[0].oracle_invoice_number
                             linked_payments.append({'id': li.id, 'invoice_reference': li.invoice_reference, 'system_identifier_id': li.system_identifier.id, 'system_identifier_system': li.system_identifier.system_id, 'booking_reference': li.booking_reference, 'booking_reference_linked': li.booking_reference_linked, 'invoice_group_id': li.invoice_group_id.id,'settlement_date': settlement_date, 'oracle_invoice_number': oracle_invoice_number})
                             if li.booking_reference not in linked_payments_booking_references:
                                linked_payments_booking_references.append(li.booking_reference)
                             if li.booking_reference_linked not in linked_payments_booking_references:
                                linked_payments_booking_references.append(li.booking_reference_linked)
                         
                         invoice_group_checks = LinkedInvoice.objects.filter(Q(booking_reference__in=linked_payments_booking_references) | Q(booking_reference_linked__in=linked_payments_booking_references)).values('invoice_group_id_id').annotate(total=Count('invoice_group_id_id')).order_by('total')
                         invoice_group_checks_total = invoice_group_checks.count()

                         invs = Invoice.objects.filter(reference__in=invoices)
                         for i in invs:
                             orders.append(i.order_number)
                             settlement_date = None
                             if i.settlement_date:
                                  settlement_date = i.settlement_date.strftime("%d/%m/%Y")
                                 
                             invoices_data.append({'invoice_reference': i.reference, 'payment_status': str(i.payment_status), 'balance': str(i.balance), 'settlement_date': settlement_date, 'amount': str(i.amount)})
                         invoice_orders = Order.objects.filter(number__in=orders)
                         order_array = []
                         order_obj = order_model.Line.objects.filter(order__number__in=orders).order_by('order__date_placed')
                         rolling_total = Decimal('0.00')
                         total_unallocated = Decimal('0.00')

                         oracle_code_totals = {}
                         data['data']['oracle_code_totals'] = {}
                         for o in order_obj:
                             owner_id = None
                             if o.order:
                                if o.order.basket:
                                    if o.order.basket.owner:
                                        owner_id = o.order.basket.owner.id

                             if o.oracle_code == 'NNP449 GST':
                                 total_unallocated = total_unallocated + o.line_price_incl_tax
                             rolling_total = rolling_total + o.line_price_incl_tax
                             row = {'id': o.id, 'order_number': o.order.number, 'title': o.title, 'line_price_incl_tax': str(o.line_price_incl_tax), 'line_price_excl_tax': str(o.line_price_incl_tax), 'owner_id': str(owner_id),'oracle_code': o.oracle_code, 'rolling_total': str(rolling_total), 'order_date': o.order.date_placed.strftime("%d/%m/%Y %H:%M:%S")}
                             order_array.append(row)

                             if o.oracle_code not in oracle_code_totals:
                                 oracle_code_totals[o.oracle_code] = Decimal('0.00')
                             oracle_code_totals[o.oracle_code] = oracle_code_totals[o.oracle_code] + o.line_price_incl_tax 

                         for cct in oracle_code_totals.keys():
                             data['data']['oracle_code_totals'][cct] = str(oracle_code_totals[cct])

                         bp_array = []
                         bp_txn_refund_hash = {}
                         bp_txn_total ={}
                         bp_trans = BpointTransaction.objects.filter(crn1__in=invoices)
                         for bp in bp_trans:
                             if bp.original_txn not in bp_txn_refund_hash:
                                   bp_txn_refund_hash[bp.original_txn] = Decimal('0.00')
                                   
                             if bp.original_txn not in bp_txn_total:
                                   bp_txn_total[bp.original_txn] = float('0.00')
                                   
                             if bp.txn_number not in bp_txn_total:
                                   bp_txn_total[bp.txn_number] = float('0.00')                                   

                             if bp.action == 'payment':
                                 bp_txn_total[bp.txn_number] = bp_txn_total[bp.txn_number] + float(bp.amount)
                                                                                                       
                             if bp.action == 'refund':
                                 bp_txn_total[bp.original_txn] = bp_txn_total[bp.original_txn] - float(bp.amount)
                                 
                                 bp_txn_refund_hash[bp.original_txn] = bp_txn_refund_hash[bp.original_txn] + bp.amount

                         total_gateway_amount = Decimal('0.00')
                         for bp in bp_trans:
                             if bp.action == 'refund':
                                 total_gateway_amount = total_gateway_amount - bp.amount
                             else:
                                 total_gateway_amount = total_gateway_amount + bp.amount

                             row = {}
                             row['id'] = bp.id
                             row['crn1'] = bp.crn1
                             row['txnnumber'] = bp.txn_number
                             row['original_txn'] = bp.original_txn
                             row['receipt_number'] = bp.receipt_number
                             row['settlement_date'] = bp.settlement_date.strftime("%d/%m/%Y")
                             row['last_digits'] = bp.last_digits
                             row['amount'] = str(bp.amount)
                             row['response_code'] = bp.response_code
                             row['action'] = bp.action
                             row['processed'] = bp.processed.strftime("%d/%m/%Y %H:%M:%S")
                             row['response_txt'] = bp.response_txt
                             if bp.action == 'payment':
                                row['amount_refunded'] = '0.00'
                                if bp.txn_number in bp_txn_refund_hash:
                                    row['amount_refunded'] = str(bp_txn_refund_hash[bp.txn_number])
                             bp_array.append(row)


                         cash_array = []
                         cash_array_invoices = {}
                         cash_txn_refund_hash = {}
                         cash_trans = CashTransaction.objects.filter(invoice__in=invs)
                         for c in cash_trans:
                             if c.id not in cash_txn_refund_hash:
                                 cash_txn_refund_hash[c.id] = Decimal('0.00')
                             if c.type == 'refund':
                                 cash_txn_refund_hash[c.id] = cash_txn_refund_hash[c.id] + c.amount
                        
                         total_cash_amount = Decimal('0.00')
                         for ch in cash_trans:
                             if ch.type  == 'refund':
                                   total_cash_amount = total_cash_amount - ch.amount
                             elif ch.type == 'payment':
                                   total_cash_amount = total_cash_amount + ch.amount

                             row = {}
                             row['id'] = ch.id
                             row['invoice_reference'] = ch.invoice.reference
                             row['amount'] = str(ch.amount)
                             row['action'] = ch.type
                             row['source'] = ch.source
                             row['receipt'] = ch.receipt
                             row['details'] = ch.details
                             row['created'] = ch.created.strftime("%d/%m/%Y %H:%M:%S")
                             
                             if ch.type == 'payment':
                                  row['amount_refunded'] = '0.00'
                                  if ch.id in cash_txn_refund_hash:
                                      row['amount_refunded'] = str(cash_txn_refund_hash[ch.id])
                             cash_array.append(row)

                         # cash group by invoice
                         for ch in cash_trans:
                             if ch.invoice.reference not in cash_array_invoices:
                                   cash_array_invoices[ch.invoice.reference] = Decimal('0.00')

                             if ch.type  == 'refund':
                                  cash_array_invoices[ch.invoice.reference] = cash_array_invoices[ch.invoice.reference] - ch.amount
                             if ch.type  == 'payment':
                                  cash_array_invoices[ch.invoice.reference] = cash_array_invoices[ch.invoice.reference] + ch.amount

                         cai = []
                         # convert decimal money to string for json dump    
                         for ca in cash_array_invoices.keys():
                               row = {}
                               row['invoice_reference'] = ca
                               row['amount'] = str(cash_array_invoices[ca])
                               cai.append(row)

                         data['data']['linked_payments'] = linked_payments
                         data['data']['total_gateway_amount'] = str(total_gateway_amount)
                         data['data']['total_oracle_amount'] = str(rolling_total)
                         data['data']['total_cash_amount'] = str(total_cash_amount)
                         data['data']['total_unallocated'] = str(total_unallocated)
                         #data['data']['oracle_code_totals']  
                         data['data']['order'] = order_array
                         data['data']['bpoint'] = bp_array
                         data['data']['cash'] = cash_array
                         data['data']['cash_on_invoices'] = cai
                         data['data']['invoices_data'] = invoices_data
                         data['data']['booking_reference'] = latest_li.booking_reference
                         data['data']['booking_reference_linked'] = latest_li.booking_reference_linked
                         data['data']['invoice_group_checks_total'] = invoice_group_checks_total
                         #data['data']['bp_txn_refund'] = bp_txn_refund_hash
                         data['data']['bp_txn_total'] = bp_txn_total
                         data['data']['invoice_group_id'] = invoice_group_id
                         data['data']['system_id'] = system_id
                         data['status'] = 200
                         exists = True
                     else:
                         data['status'] = 404
                         data['message'] =  "No records found"
                         data['data']['linked_payments'] = []
                         data['data']['total_gateway_amount'] = '0.00'
                         data['data']['total_unallocated'] = '0.00'
                         data['data']['total_oracle_amount'] = '0.00'
                         data['data']['order'] = []
                         data['data']['bpoint'] = []
                         data['data']['booking_reference'] = ''
                         data['data']['booking_reference_linked'] = ''
                         data['data']['bp_txn_total'] = {}

        else:
            data['status'] = 404
            data['message'] =  "No records found"
            data['data']['linked_payments'] = []
            data['data']['total_gateway_amount'] = '0.00'
            data['data']['total_unallocated'] = '0.00'
            data['data']['total_oracle_amount'] = '0.00'
            data['data']['order'] = []
            data['data']['bpoint'] = []
            data['data']['booking_reference'] = ''
            data['data']['booking_reference_linked'] = ''
            
        return data

def get_oracle_interface_system_permissions(system_id, email):

    system_interface_permssions = {
        'all_access': False,
        'view_ledger_tools' : False,
        'manage_ledger_tool' : False,
        'view_payment_totals' : False,
    }

    ois = OracleInterfaceSystem.objects.filter(system_id=system_id) 
    if ois.count() > 0:
        ois_permissions = OracleInterfacePermission.objects.filter(system=ois[0],email=email)
        for oisp in ois_permissions:
            if oisp.access_type == 'all_access':
                system_interface_permssions['all_access'] = True
            if oisp.access_type == 'view_ledger_tools':
                system_interface_permssions['view_ledger_tools'] = True
            if oisp.access_type == 'manage_ledger_tool':
                system_interface_permssions['manage_ledger_tool'] = True                
            if oisp.access_type == 'view_payment_totals':
                system_interface_permssions['view_payment_totals'] = True                  
    return system_interface_permssions



