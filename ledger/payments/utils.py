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
from ledger.payments.models import OracleParser, OracleParserInvoice, Invoice, OracleInterface, OracleInterfaceSystem, BpointTransaction, BpayTransaction, OracleAccountCode,OracleOpenPeriod 
from oscar.core.loading import get_class
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
        resp = requests.get(url)
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
        if not error_email:
            dt = datetime.datetime.strptime(trans_date,'%Y-%m-%d').strftime('%d/%m/%Y')
            _file = generateOracleParserFile(oracle_codes)
            email = EmailMessage(
                'Oracle Interface for {} for transactions received on {}'.format(system_name,dt),
                'Oracle Interface Summary File for {} for transactions received on {}'.format(system_name,dt),
                settings.EMAIL_FROM,
                to=[r.email for r in recipients]if recipients else [settings.NOTIFICATION_EMAIL]
            )
            email.attach('OracleInterface_{}.csv'.format(dt), _file.getvalue(), 'text/csv')
        else:
            dt = datetime.datetime.strptime(trans_date,'%Y-%m-%d').strftime('%d/%m/%Y')
            today = datetime.datetime.now().strftime('%d/%m/%Y')
            subject = 'Oracle Interface Error for {} for transactions received on {}'.format(system_name,dt)
            email = EmailMessage(subject,
                'There was an error in generating a summary report for the oracle interface parser for transactions processed on {}.Please refer to the following log output:\n\n\n{}'.format(today,error_string),
                settings.EMAIL_FROM,
                to=[r.email for r in recipients]if recipients else [settings.NOTIFICATION_EMAIL]
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
        new_codes = {}
        if not override:
            try:
                OracleOpenPeriod.objects.get(period_name=oracle_date)
            except OracleOpenPeriod.DoesNotExist:
                raise ValidationError('There is currently no open period for transactions done on {}'.format(trans_date))

        for k,v in oracle_codes.items():
            if v != 0:
                found = OracleAccountCode.objects.filter(active_receivables_activities=k)
                if not found:
                    raise ValidationError('{} is not a valid account code'.format(k)) 

                # Check if there is a deduction for that system/account code, and sends to another oracle account code
                deduction = OracleInterfaceDeduction.objects.filter(oisystem=system, percentage_account_code=k).first()

                if deduction and system.deduct_percentage:
                    
                    if (not deduction.percentage or not deduction.destination_account_code):
                            raise Exception('Deduction Percentage and an oracle account are required if deduction is enabled.')

                    deduction_code = None
                    try:
                        OracleAccountCode.objects.filter(active_receivables_activities=deduction.destination_account_code)
                    except OracleAccountCode.DoesNotExist:
                        raise ValidationError('The account code setup for oracle deduction does not exist.')
                    # Add the deducted amount to the oracle code specified in the system table
                    deduction_code = OracleInterface(
                        receipt_date = trans_date,
                        activity_name = deduction.destination_account_code,
                        amount = D(0.0), 
                        customer_name = system.system_name,
                        description = deduction.destination_account_code,
                        source = system.source,
                        method = system.method,
                        comments = '{} GST/{}'.format(deduction.destination_account_code,date),
                        status = 'NEW',
                        status_date = today
                    )
                    deduction_code.save()

                    initial_amount = D(v)
                    remainder_amount = ((100 - deduction.percentage)/ D(100)) * initial_amount
                    deduction_code.amount += initial_amount - remainder_amount
                    # Add the remainaing amount to the intial oracle account code
                    OracleInterface.objects.create(
                        receipt_date = trans_date,
                        activity_name = k,
                        amount = remainder_amount,
                        customer_name = system.system_name,
                        description = k,
                        source = system.source,
                        method = system.method,
                        comments = '{} GST/{}'.format(k,date),
                        status = 'NEW',
                        status_date = today
                    )
                    new_codes[k] = remainder_amount 
                else:
                    OracleInterface.objects.create(
                        receipt_date = trans_date,
                        activity_name = k,
                        amount = v,
                        customer_name = system.system_name,
                        description = k,
                        source = system.source,
                        method = system.method,
                        comments = '{} GST/{}'.format(k,date),
                        status = 'NEW',
                        status_date = today
                    )
                    new_codes[k] = v

        if system.deduct_percentage and deduction_code.amount != 0:
            deduction_code.save()
            new_codes[deduction_code.activity_name] = deduction_code.amount
        return new_codes
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

def update_payments(invoice_reference):
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
