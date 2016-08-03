import csv
import datetime
import StringIO
from models import Invoice

def generate_csv(system,start,end):
    # Get invoices matching the system and date range
    strIO = None
    invoices = Invoice.objects.filter(system=system)
    if invoices:
        strIO = StringIO.StringIO()
        fieldnames = ['Created','Method','Transaction Type','Amount','Status','Source','Product Names','Product Codes']
        writer = csv.DictWriter(strIO,fieldnames=fieldnames)
        writer.writeheader()
        for i in invoices:
            items = item_codes = bpay = bpoint = cash = None
            item_names = []
            oracle_codes = []
            # Get all items for this invoice
            if i.order:
                items = i.order.lines.all().values('title','oracle_code')
                for item in items:
                    item_names.append(item.get('title'))
                    code = item.get('oracle_code')
                    if not code: code = 'N\A'
                    oracle_codes.append(code)
                item_names = '|'.join(item_names)
                oracle_codes = '|'.join(oracle_codes)
            # Get all transactions for this invoice
            cash = i.cash_transactions.filter(created__gte=start,created__lte=end+datetime.timedelta(days=1))
            bpoint = i.bpoint_transactions.filter(created__gte=start,created__lte=end+datetime.timedelta(days=1))
            bpay = i.bpay_transactions.filter(p_date__gte=start,p_date__lte=end+datetime.timedelta(days=1))
            # Write out the cash transactions
            for c in cash:
                cash_info = {
                    'Created':c.created.strftime('%Y-%m-%d'),
                    'Method': 'Cash',
                    'Transaction Type':c.type.lower(),
                    'Amount':c.amount,
                    'Status':'True',
                    'Source':c.source,
                    'Product Names': item_names,
                    'Product Codes': oracle_codes
                }
                writer.writerow(cash_info)
            # Write out all bpay transactions
            for b in bpay:
                bpay_info = {
                    'Created':b.created.strftime('%Y-%m-%d'),
                    'Method': 'BPAY',
                    'Transaction Type':b.get_p_instruction_code_display(),
                    'Amount':b.amount,
                    'Status':b.approved,
                    'Source':'N/A',
                    'Product Names': item_names,
                    'Product Codes': oracle_codes
                }
                writer.writerow(bpay_info)
            # Write out all bpoint transactions
            for bpt in bpoint:
                #print item_names
                bpoint_info = {
                    'Created':bpt.created.strftime('%Y-%m-%d'),
                    'Method': 'BPOINT',
                    'Transaction Type':bpt.action.lower(),
                    'Amount':bpt.amount,
                    'Status':bpt.approved,
                    'Source':'N/A',
                    'Product Names': item_names,
                    'Product Codes': oracle_codes
                }
                writer.writerow(bpoint_info)
        strIO.flush()
        strIO.seek(0)
            
    return strIO
            
        
        
    
