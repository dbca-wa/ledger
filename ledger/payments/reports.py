import StringIO
import csv

from models import Invoice


def generate_csv(system, start, end):
    # Get invoices matching the system and date range
    strIO = None
    invoices = Invoice.objects.filter(system=system)
    if invoices:
        strIO = StringIO.StringIO()
        fieldnames = ['Created', 'Payment Method', 'Transaction Type', 'Amount', 'Approved', 'Source', 'Product Names',
                      'Product Codes']
        writer = csv.DictWriter(strIO, fieldnames=fieldnames)
        writer.writeheader()
        for i in invoices:
            items = item_codes = bpay = bpoint = cash = None
            item_names = []
            oracle_codes = []
            # Get all items for this invoice
            if i.order:
                items = i.order.lines.all().values('title', 'oracle_code')
                for item in items:
                    item_names.append(item.get('title'))
                    code = item.get('oracle_code')
                    if not code: code = 'N\A'
                    oracle_codes.append(code)
                item_names = '|'.join(item_names)
                oracle_codes = '|'.join(oracle_codes)
            # Get all transactions for this invoice
            cash = i.cash_transactions.filter(created__gte=start, created__lte=end)
            bpoint = i.bpoint_transactions.filter(created__gte=start, created__lte=end)
            bpay = i.bpay_transactions.filter(p_date__gte=start, p_date__lte=end)
            # Write out the cash transactions
            for c in cash:
                cash_info = {
                    'Created': c.created.strftime('%Y-%m-%d'),
                    'Payment Method': 'Cash',
                    'Transaction Type': c.type.lower(),
                    'Amount': c.amount,
                    'Approved': 'True',
                    'Source': c.source,
                    'Product Names': item_names,
                    'Product Codes': oracle_codes
                }
                writer.writerow(cash_info)
            # Write out all bpay transactions
            for b in bpay:
                bpay_info = {
                    'Created': b.created.strftime('%Y-%m-%d'),
                    'Payment Method': 'BPAY',
                    'Transaction Type': b.get_p_instruction_code_display(),
                    'Amount': b.amount,
                    'Approved': b.approved,
                    'Source': 'N/A',
                    'Product Names': item_names,
                    'Product Codes': oracle_codes
                }
                writer.writerow(bpay_info)
            # Write out all bpoint transactions
            for bpt in bpoint:
                bpoint_info = {
                    'Created': bpt.created.strftime('%Y-%m-%d'),
                    'Payment Method': 'BPOINT',
                    'Transaction Type': bpt.action.lower(),
                    'Amount': bpt.amount,
                    'Approved': bpt.approved,
                    'Source': 'N/A',
                    'Product Names': item_names,
                    'Product Codes': oracle_codes
                }
                writer.writerow(bpoint_info)
        strIO.flush()
        strIO.seek(0)
    return strIO
