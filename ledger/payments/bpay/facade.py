import datetime
import traceback
import csv
import logging
import pytz
from six.moves import StringIO
from os import listdir
from os.path import isfile, join
from decimal import Decimal
from django.db import IntegrityError, transaction
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from ledger.payments.bpay.models import *
from ledger.payments.bpay.crn import getCRN
from ledger.payments.utils import update_payments

logging.info('Starting logger for BPAY.')
logger = logging.getLogger(__name__)

def get_file(file_name):
    '''Open the file to be parsed.
    '''
    f = open(file_name, 'rt')
    
    return f

def record_grouprec(row,_file):
    '''
        Make a new Bpay Group Record
    '''
    return BpayGroupRecord(
        settled = validate_datetime(row[4],row[5]),
        modifier = row[7].replace('/',''),
        file = _file
    )

def record_accounttrailer(row,_file):
    '''
        Make a new Bpay Account Trailer Record
    '''
    return BpayAccountTrailer(
        total = '{0}.{1}'.format(row[1][:-2],row[1][-2:]),
        records = row[2].replace('/',''),
        file = _file
    )

def record_grouptrailer(row, _file):
    '''
        Make a new Bpay Group Trailer Record
    '''
    return BpayGroupTrailer(
        total = '{0}.{1}'.format(row[1][:-2],row[1][-2:]),
        accounts = row[2],
        records = row[3].replace('/',''),
        file = _file
    )

def record_filetrailer(row,_file):
    '''
        Make a new Bpay File Trailer Record
    '''
    return BpayFileTrailer(
        total = '{0}.{1}'.format(row[1][:-2],row[1][-2:]),
        groups = row[2],
        records = row[3].replace('/',''),
        file = _file
    )
def record_accountrec(row,_file):
    '''
        Make a new Bpay Account Record
    '''
    return BpayAccountRecord(
        credit_items = row[5],
        credit_amount = check_amount(row[4]),
        cheque_items = row[9],
        cheque_amount = check_amount(row[8]),
        debit_items = row[13],
        debit_amount = check_amount(row[12]),
        file = _file
    )

def record_txn(row,_file):
    '''
        Make a new Bpay Transaction object
    '''
    return BpayTransaction(
        amount = '{0}.{1}'.format(row[2][:-2],row[2][-2:]),
        type = row[1],
        cheque_num = row[3],
        crn = row[4],
        original_crn = row[4],
        txn_ref = row[5],
        service_code = row[6],
        p_instruction_code = row[7],
        p_method_code = row[8],
        p_date = validate_datetime(row[9], row[10], with_seconds=True),
        entry_method = row[11],
        orig_ref_num = row[12],
        ref_rev_code = row[13],
        discretionary_data = row[14],
        payer_name = row[15],
        country = row[16],
        state = row[17],
        car = row[18],
        discount_ref = row[19],
        discount_method = row[20].replace('/',''),
        biller_code = row[21],
        file = _file
    )

def validate_datetime(_date,_time,with_seconds=False):
    '''Changing the date and time to UTC.
        Combining the date and time and converting it to UTC.
    '''
    valid_time = valid_datetime = valid_date = None
    
    time_zone = pytz.timezone('Australia/Sydney')
    valid_date = datetime.datetime.strptime(_date, '%Y%m%d').date()
    if with_seconds:
        if _time:
            valid_time =  datetime.datetime.strptime(_time, '%H%M%S').time()
    else:
        if _time:
            valid_time =  datetime.datetime.strptime(_time, '%H%M').time()
    
    if valid_time:
        valid_datetime = datetime.datetime.combine(valid_date, valid_time)
    else:
        valid_datetime = datetime.datetime.combine(valid_date, datetime.datetime.min.time())
    valid_datetime = time_zone.localize(valid_datetime)
    
    return valid_datetime.astimezone(pytz.utc)
    
def check_amount(value):
    '''Separate the amount since it is stored as
        an unassigned integer with the last two values
        denoting the cents.
    '''
    if value:
        return Decimal('{0}.{1}'.format(value[:-2],value[-2:]))
    return Decimal('0')

def checkStepValue(value):
    if len(value) == 1:
        return '0{}'.format(value)
    return value

def validate_file(f):
    '''Check if the specified file is valid.
    '''
    # Validate steps
    steps = {
        '01': 1,
        '02': 2,
        '03': 3,
        '30': 4,
        '49': 5,
        '98': 6,
        '99': 7
    }
    steps_count = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
        7: 0
    }
    step_column_length = {
        1: 9,
        2: 8,
        3: 15,
        4: 21,
        5: 3,
        6: 4,
        7: 4
    }
    prev_step = 0
    current_step = 0
    error = None
    line = 1
    row_count = 0
    try:
        reader = csv.reader(f)
        for row in reader:
            if row:
                # Get current step value and check if it one step ahead of previous step.
                current_step = steps.get(checkStepValue(row[0]))
                # Count the number of record in the file
                steps_count[current_step] += 1
                    
                # Get current step valid column number
                if len(row) != step_column_length.get(current_step):
                    error = 'An error occured at line {0}: Check this line and make sure that it meets the required length of {1}.'.format(line, step_column_length.get(current_step))
                    logger.error(error)
                    raise Exception(error)
            line += 1
            row_count += 1
        if row_count > 2:
            for k,v in steps_count.items():
                if v < 1:
                    error = 'An error occured at line {0}: Ensure that the file contains all the record types.'.format(line)
                    logger.error(error)
                    raise Exception(error)
            
    except:
        raise

def parseFile(file_path):
    '''Parse the file in order to create the relevant
        objects.
    '''
    from ledger.payments.models import Invoice
    f = get_file(file_path)
    transaction_list, group_list, account_list = [], [], []
    transaction_rows, group_rows, account_rows  = [], [], []
    accountttrailer_rows, grouptrailer_rows, filetrailer_row = [], [], None
    accountttrailer_list, grouptrailer_list = [], []
    bpay_file = None
    success = True
    biller_code = None
    try:
        # Validate the file first
        validate_file(f)
        f.seek(0)
        reader = csv.reader(f)
        # Instanciate a new Bpay File
        bpay_file = BpayFile()
        for row in reader:
            if row:
                if checkStepValue(row[0]) == '01':
                    # Format the time to 24h
                    bpay_file.created = validate_datetime(row[3],row[4])
                    bpay_file.file_id = row[5]
                elif checkStepValue(row[0]) == '02':
                    biller_code = row[1]
                    group_rows.append(row)
                elif checkStepValue(row[0]) == '03':
                    account_rows.append(row)
                elif checkStepValue(row[0]) == '30':
                    if row[11] not in ['APF','LBX']:
                        #transaction_list.append(record_txn(row,bpay_file))
                        row.append(biller_code)
                        transaction_rows.append(row)
                elif checkStepValue(row[0]) == '49':
                    accountttrailer_rows.append(row)
                elif checkStepValue(row[0]) == '98':
                    grouptrailer_rows.append(row)
                elif checkStepValue(row[0]) == '99':
                    filetrailer_row = row

        with transaction.atomic():
            bpay_file.save()
            # Create Group Records
            for row in group_rows:
                group_list.append(record_grouprec(row,bpay_file))
            # Create Account Records
            for row in account_rows:
                account_list.append(record_accountrec(row,bpay_file))
            # Create transactions
            for row in transaction_rows:
                transaction_list.append(record_txn(row,bpay_file))
            # Create Account Trailer Records
            for row in accountttrailer_rows:
                accountttrailer_list.append(record_accounttrailer(row,bpay_file))
            # Create Group Trailer Records
            for row in grouptrailer_rows:
                grouptrailer_list.append(record_grouptrailer(row,bpay_file))
            # Store Records
            BpayGroupRecord.objects.bulk_create(group_list)
            BpayAccountRecord.objects.bulk_create(account_list)
            BpayTransaction.objects.bulk_create(transaction_list)
            BpayAccountTrailer.objects.bulk_create(accountttrailer_list)
            BpayGroupTrailer.objects.bulk_create(grouptrailer_list)
            # Create File Trailer Record
            record_filetrailer(filetrailer_row,bpay_file).save()

            # Update payments in the new transaction invoices
            for t in bpay_file.transactions.all():
                try:
                    inv = Invoice.objects.get(reference=t.crn)
                    update_payments(inv.reference)
                except Invoice.DoesNotExist:
                    pass
        return success,bpay_file,''
    except IntegrityError as e:
        success = False
        return success,None,e.message
    except Exception as e:
        traceback.print_exc()
        success = False
        return success,None,e.message
    finally:
        f.close()

def getfiles(path):
    files = []
    try:
        files = [[join(path, f),f] for f in listdir(path) if isfile(join(path, f)) and f.startswith('BPAY')]
    except Exception as e:
        raise
    return files

def generateParserSummary(files):
    valid = files['valid']
    other = files['other']
    failed = files['failed']
    processed = files['processed']

    output = StringIO()
    output.write('Successful Files with transactions:\n')
    # Successful Files
    for n,t in valid:
        output.write('  File Name: {}\n'.format(n))
        output.write('    Transactions:\n')
        for trans in t.transactions.all():
            output.write('      CRN: {}\n'.format(trans.crn))
    # Successful Files without transactions
    output.write('\nSuccessful Files without transactions:\n')
    for n,t in other:
        output.write('  File Name: {}\n'.format(n))
    # Failed files
    output.write('\nFailed Files:\n')
    for n,r in failed:
        output.write('  File Name: {}\n'.format(n))
        output.write('    Reason: {}\n'.format(r))
    # Already processed Files
    output.write('\nFiles previously processed:\n')
    for n,t in processed:
        output.write('  File Name: {}\n'.format(n))

    contents = output.getvalue()
    output.close()
    return contents

def sendSummaryEmail(summary):
    dt = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    recipients = BpayJobRecipient.objects.all()
    email = EmailMessage(
        'BPAY Summary {}'.format(dt),
        'BPAY Summary File for {}'.format(dt),
        settings.EMAIL_FROM,
        to=[r.email for r in recipients]if recipients else [settings.NOTIFICATION_EMAIL]
    )
    email.attach('summary.txt', summary, 'text/plain')
    email.send()
    
def sendBillerCodeEmail(summaries,monthly=False):
    emails = []
    dt = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    for k,v in summaries.items():
        try:
            sys = BillerCodeSystem.objects.get(biller_code=k)
            recipients = [x.email for x in sys.recipients.all()]
            
            if not monthly:
                subject = 'BPAY Summary: Biller Code {} as at {}'.format(k,dt)
                content = 'BPAY Transaction Summary File for Biller Code {} as at {}'.format(k,dt)
            else:
                subject = 'Monthly BPAY Report for unmatched payments for Biller Code {} as at {}'.format(k,dt)
                content = 'Monthly BPAY Transaction Report for unmatched payments for Biller Code {} as at {}'.format(k,dt)
            
            email = EmailMessage(
                subject,
                content,
                settings.EMAIL_FROM,
                to= recipients
            )
            email.attach('summary.txt', v, 'text/plain')
            emails.append(email)
        except BillerCodeSystem.DoesNotExist:
            pass
        
    connection = get_connection()
    connection.send_messages(emails)
    

def generateTransactionsSummary(files,unmatched_only=False):
    try:
        # Split transactions into biller codes
        biller_codes = {}
        biller_code_emails = {}
        if unmatched_only:
            for f in files:
                for t in f.transactions.all():
                    if t.biller_code in biller_codes:
                        txns = list(biller_codes[t.biller_code])
                        txns.append(t)
                        biller_codes[t.biller_code] = txns
                    else:
                        biller_codes[t.biller_code] = [t]
        else:
            for n, f in files:
                for t in f.transactions.all():
                    if t.biller_code in biller_codes:
                        txns = list(biller_codes[t.biller_code])
                        txns.append(t)
                        biller_codes[t.biller_code] = txns
                    else:
                        biller_codes[t.biller_code] = [t]
        # Generate summaries per biller code
        for k,v in biller_codes.items():
            matched = []
            unmatched = []
            for t in v:
                if t.matched:
                    matched.append(t)
                else:
                    unmatched.append(t)
            output = StringIO()
            if not unmatched_only:
                # Matched txns
                output.write('Matched transactions:\n')
                for m in matched:
                    output.write('  CRN: {} Amount: ${}\n'.format(m.crn,m.amount))
            # Unmatched txns
            output.write('\nUnmatched transactions:\n')
            for u in unmatched:
                output.write('  CRN: {} Amount: ${}\n'.format(u.crn,u.amount))
            
            contents = output.getvalue()
            output.close()
            # Add the biller code email
            biller_code_emails[k] = contents
        return biller_code_emails
    except Exception as e:
        traceback.print_exc(e)
        raise

def monthlyReport():
    files =  BpayFile.objects.all()
    sendBillerCodeEmail(generateTransactionsSummary(files,unmatched_only=True),monthly=True)

def bpayParser(path):
    files = getfiles(path)
    valid_files = []
    failed_files = []
    other_files = []
    processed_files = []
    try:
        if settings.NOTIFICATION_EMAIL:
            for p,n in files:
                status,bfile,reason = parseFile(p)
                if bfile is not None:
                    if bfile.transactions.all():
                        valid_files.append([n,bfile])
                    else:
                        other_files.append([n,bfile])
                else:
                    if 'unique constraint' in reason:
                        processed_files.append([n,'processed'])
                    else:
                        failed_files.append([n,reason])

            summary = generateParserSummary({
                'valid': valid_files,
                'failed': failed_files,
                'other': other_files,
                'processed': processed_files
            })
            sendSummaryEmail(summary)
            sendBillerCodeEmail(generateTransactionsSummary(valid_files))
        else:
            raise Exception('NOTIFICATION_EMAIL is not set.')
    except:
        raise
