import StringIO
import csv
from datetime import timedelta
from decimal import Decimal as D
from models import Invoice, CashTransaction

def daterange(start,end):
    for n in range(int ((end-start).days) + 1):
        yield start + timedelta(n)

def generate_items_csv(system,start,end,region=None,district=None):
    strIO = None
    invoices = Invoice.objects.filter(system=system)
    dates = []
    date_amounts = []
    items = []
    date_format = '%A %d/%m/%y'
    if invoices:
        strIO = StringIO.StringIO()
        fieldnames = ['Account Code', 'Day']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)
        
        for d in daterange(start,end):
            dates.append(d.strftime(date_format))
            date_amounts.append({
                'date':d.strftime(date_format),
                'amounts':{
                    'card': D('0.0'),
                    'bpay': D('0.0'),
                    'eft': D('0.0'),
                    'cash': D('0.0'),
                    'cheque': D('0.0'),
                    'money_order': D('0.0')
                }
            })
        dates_row = ''
        for date in dates:
            dates_row += '{},,,,,,'.format(date)
        
        # Dates row
        writer.writerow(['']+ dates_row.split(','))
        writer.writerow([''] + ['Credit Card','Bpay','EFTPOS','Cash','Cheque','Money Order'] * len(dates) + ['','Credit Card','Bpay','EFTPOS','Cash','Cheque','Money Order','Banked(Cash,Money Order,Cheque)'])
        for i in invoices:
            # Add items of invoice if not in list
            if i.order:
                for x in i.order.lines.all():
                    item_date_amounts = []
                    for d in dates:
                        item_date_amounts.append({
                            'date':d,
                            'amounts':{
                                'card': D('0.0'),
                                'bpay': D('0.0'),
                                'eft': D('0.0'),
                                'cash': D('0.0'),
                                'cheque': D('0.0'),
                                'money_order': D('0.0')
                            }
                        })
                    
                    if not any(it.get('item', None).oracle_code == x.oracle_code for it in items):
                        items.append({
                            'dates':item_date_amounts,
                            'item': x,
                            'card': D('0.0'),
                            'bpay': D('0.0'),
                            'eft': D('0.0'),
                            'cash': D('0.0'),
                            'cheque': D('0.0'),
                            'money_order': D('0.0')
                        })
            # Get all transactions
            cash = i.cash_transactions.filter(created__gte=start, created__lte=end, district=district)
            bpoint = i.bpoint_transactions.filter(created__gte=start, created__lte=end)
            bpay = i.bpay_transactions.filter(p_date__gte=start, p_date__lte=end)
            # Go through items
            
            for item in items:
                for d in item['dates']:
                    # Cash
                    index = 0
                    for l in date_amounts:
                        if l.get('date') == d.get('date'):
                            date_amount_index = index
                            break
                        index += 1
                    for c in cash:
                        for s in CashTransaction.SOURCE_TYPES:
                            source = str(s[0])
                            if c.source == source:
                                if c.created.strftime(date_format) == d.get('date'):
                                    if c.type == 'payment':
                                        d['amounts'][source] += D(item.get('item').line_price_before_discounts_incl_tax)
                                        item[source] += D(item.get('item').line_price_before_discounts_incl_tax)
                                        date_amounts[date_amount_index]['amounts'][source] += D(item.get('item').line_price_before_discounts_incl_tax)
                                    else:
                                        d['amounts'][source] -= D(item.get('item').line_price_before_discounts_incl_tax)
                                        item[source] -= D(item.get('item').line_price_before_discounts_incl_tax)
                                        date_amounts[date_amount_index]['amounts'][source] -= D(item.get('item').line_price_before_discounts_incl_tax)
                    # Card
                    for c in bpoint:
                        if c.approved:
                            if c.created.strftime(date_format) == d.get('date'):
                                if c.action == 'payment' or c.action == 'capture':
                                    d['amounts']['card'] += D(item.get('item').line_price_before_discounts_incl_tax)
                                    item['card'] += D(item.get('item').line_price_before_discounts_incl_tax)
                                    date_amounts[date_amount_index]['amounts']['card'] += D(item.get('item').line_price_before_discounts_incl_tax)
                                elif c.action == 'reversal' or c.action == 'refund':
                                    d['amounts']['card'] -= D(item.get('item').line_price_before_discounts_incl_tax)
                                    item['card'] -= D(item.get('item').line_price_before_discounts_incl_tax)
                                    date_amounts[date_amount_index]['amounts']['card'] -= D(item.get('item').line_price_before_discounts_incl_tax)
                    # BPAY
                    for b in bpay:
                        if b.approved:
                            if b.p_date.strftime(date_format) == d.get('date'):
                                if b.p_instruction_code == '05' and b.type == '399':
                                    d['amounts']['bpay'] += D(item.get('item').line_price_before_discounts_incl_tax)
                                    item['bpay'] += D(item.get('item').line_price_before_discounts_incl_tax)
                                    date_amounts[date_amount_index]['amounts']['bpay'] += D(item.get('item').line_price_before_discounts_incl_tax)
                                elif b.p_instruction_code == '25' and b.type == '699':
                                    d['amounts']['bpay'] += D(item.get('item').line_price_before_discounts_incl_tax)
                                    item['bpay'] -= D(item.get('item').line_price_before_discounts_incl_tax)
                                    date_amounts[date_amount_index]['amounts']['bpay'] -= D(item.get('item').line_price_before_discounts_incl_tax)
        for i in items:
            item_str = ''
            item_str += '{},'.format(str(i.get('item').oracle_code))
            for d in i['dates']:
                item_str += '{},{},{},{},{},{},'.format(d['amounts']['card'],d['amounts']['bpay'],d['amounts']['eft'],d['amounts']['cash'],d['amounts']['cheque'],d['amounts']['money_order'])
            item_str += ',{},{},{},{},{},{},{}'.format(i['card'],i['bpay'],i['eft'],i['cash'],i['cheque'],i['money_order'],sum([i['cash'],i['cheque'],i['money_order']]))
            writer.writerow(item_str.split(','))

        total_str = 'Totals,'
        total_amounts = {
            'card': D('0.0'),
            'bpay': D('0.0'),
            'eft': D('0.0'),
            'cash': D('0.0'),
            'cheque': D('0.0'),
            'money_order': D('0.0')
        }
        for d in date_amounts:
            total_amounts['card'] += d['amounts']['card']
            total_amounts['bpay'] += d['amounts']['bpay']
            total_amounts['eft'] += d['amounts']['eft']
            total_amounts['cash'] += d['amounts']['cash']
            total_amounts['cheque'] += d['amounts']['cheque']
            total_amounts['money_order'] += d['amounts']['money_order']
            total_str += '{},{},{},{},{},{},'.format(d['amounts']['card'],d['amounts']['bpay'],d['amounts']['eft'],d['amounts']['cash'],d['amounts']['cheque'],d['amounts']['money_order'])
        total_str += ',{},{},{},{},{},{},'.format(total_amounts['card'],total_amounts['bpay'],total_amounts['eft'],total_amounts['cash'],total_amounts['cheque'],total_amounts['money_order'])
        total_str += '{},'.format(sum([total_amounts['cash'],total_amounts['cheque'],total_amounts['money_order']]))
        writer.writerow('')
        writer.writerow(total_str.split(','))
        strIO.flush()
        strIO.seek(0)
    return strIO
        
def generate_trans_csv(system,start,end,region=None,district=None):
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
            '''params = {
                'created__gte':start,
                'created__lte': end
            }'''
            cash = i.cash_transactions.filter(created__gte=start, created__lte=end, district=district)
            if not district:
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
            if not district:
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
