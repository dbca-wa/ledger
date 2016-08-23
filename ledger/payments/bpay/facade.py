import datetime
import logging
import pytz
from models import *
from crn import getCRN
import csv
from decimal import Decimal

logging.info('Starting logger for BPAY.')
logger = logging.getLogger(__name__)

def get_file(file_name):
    '''Open the file to be parsed.
    '''
    f = open(file_name, 'rt')
    
    return f

def record_txn(row,_file):
    '''
        Make a new Bpay Transaction object
    '''
    return BpayTransaction(
        amount = '{0}.{1}'.format(row[2][:-2],row[2][-2:]),
        type = row[1],
        cheque_num = row[3],
        crn = row[4],
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
    step_column_length = {
        1: 9,
        2: 8,
        3: 15,
        4: 21,
        5: 3,
        6: 4,
        7: 4
    }
    prev_step = current_step = 0
    error = None
    line = 1
    try:
        reader = csv.reader(f)
        for row in reader:
            # Get current step value and check if it one step ahead of previous step.
            current_step = steps.get(row[0])
            # Check if it is the transaction row since there may be multiple of them.
            if current_step == 4 and prev_step == 4:
                pass
            elif (current_step - 1) == prev_step:
                prev_step = current_step
            else:
                error = 'An error occured at line {0}: Ensure that the file contains all the record types.'.format(line)
                logger.error(error)
                raise Exception(error)
            # Get current step valid column number
            if len(row) != step_column_length.get(current_step):
                error = 'An error occured at line {0}: Check this line and make sure that it meets the required length of {1}.'.format(line, step_column_length.get(current_step))
                logger.error(error)
                raise Exception(error)
            line += 1
            
    except:
        raise

def parseFile(file_path='/mnt/storage/Apps/ledger/ledger/payments/bpay/dpaw.csv'):
    '''Parse the file in order to create the relevant
        objects.
    '''
    f = get_file(file_path)
    transaction_list = []
    bpay_file = None
    try:
        # Validate the file first
        validate_file(f)
        f.seek(0)
        reader = csv.reader(f)
        # Instanciate a new Bpay File
        bpay_file = BpayFile()
        for row in reader:
            if row[0] == '01':
                bpay_file.created = validate_datetime(row[3],row[4])
                bpay_file.file_id = row[5]
            elif row[0] == '02':
                bpay_file.settled = validate_datetime(row[4],row[5])
                bpay_file.date_modifier = row[7].replace('/','')
            elif row[0] == '03':
                bpay_file.credit_items = row[5]
                bpay_file.credit_amount = check_amount(row[4])
                bpay_file.cheque_items = row[9]
                bpay_file.cheque_amount = check_amount(row[8])
                bpay_file.debit_items = row[13]
                bpay_file.debit_amount = check_amount(row[12])
                # Save the file in order to use on the transactions
                bpay_file.save()
            elif row[0] == '30':
                if row[11] not in ['APF','LBX']:
                    transaction_list.append(record_txn(row,bpay_file))
            elif row[0] == '49':
                bpay_file.account_total = '{0}.{1}'.format(row[1][:-2],row[1][-2:])
                bpay_file.account_records = row[2].replace('/','')
            elif row[0] == '98':
                bpay_file.group_total = '{0}.{1}'.format(row[1][:-2],row[1][-2:])
                bpay_file.group_accounts = row[2]
                bpay_file.group_records = row[3].replace('/','')
            elif row[0] == '99':
                bpay_file.file_total = '{0}.{1}'.format(row[1][:-2],row[1][-2:])
                bpay_file.file_groups = row[2]
                bpay_file.file_records = row[3].replace('/','')
        bpay_file.save()
        BpayTransaction.objects.bulk_create(transaction_list)
        
        return bpay_file
    except Exception as e:
        print str(e)
    finally:
        f.close()