from six.moves import StringIO
import csv
import pytz
from datetime import timedelta,datetime
from decimal import Decimal as D
from ledger.payments.models import Invoice, CashTransaction, BpointTransaction, BpayTransaction
from ledger.order.models import Line

PERTH_TIMEZONE = pytz.timezone('Australia/Perth')

def daterange(start,end):
    for n in range(int ((end-start).days) + 1):
        yield start + timedelta(n)

def generate_items_csv(system,start,end,banked_start,banked_end,region=None,district=None):
    strIO = None
    invoices = []
    invoice_list = []
    dates, banked_dates = [], []
    date_amounts, banked_date_amounts = [], []
    items = []
    oracle_codes = {}
    banked_oracle_codes = {}
    date_format = '%d/%m/%y'

    eftpos = []
    banked_cash = []
    bpoint = []
    bpay = []

    # Get all transactions
    if not district:
        eftpos.extend([x for x in CashTransaction.objects.filter(created__gte=start, created__lte=end, source='eftpos').exclude(district__isnull=False)])
        banked_cash.extend([x for x in CashTransaction.objects.filter(created__gte=banked_start, created__lte=banked_end).exclude(source='eftpos').exclude(district__isnull=False)])
        bpoint.extend([x for x in BpointTransaction.objects.filter(settlement_date__gte=start, settlement_date__lte=end).exclude(crn1__endswith='_test')])
        bpay.extend([x for x in BpayTransaction.objects.filter(p_date__gte=start, p_date__lte=end)])
    else:
        eftpos.extend([x for x in CashTransaction.objects.filter(created__gte=start, created__lte=end, source='eftpos',district=district)])
        banked_cash.extend([x for x in CashTransaction.objects.filter(created__gte=banked_start, created__lte=banked_end,district=district).exclude(source='eftpos')])

    # Get the required invoices
    for e in eftpos:
        if e.invoice.reference not in invoice_list:
            if e.invoice.system == system:
                invoices.append(e.invoice)
                invoice_list.append(str(e.invoice.reference))
    for b in banked_cash:
        if b.invoice.reference not in invoice_list:
            if b.invoice.system == system:
                invoices.append(b.invoice)
                invoice_list.append(str(b.invoice.reference))
    for b in bpoint:
        if b.crn1 not in invoice_list:
            invoice = Invoice.objects.get(reference=b.crn1)
            if invoice.system == system:
                invoices.append(invoice)
                invoice_list.append(str(b.crn1))
    for b in bpay:
        if b.crn not in invoice_list:
            invoice = Invoice.objects.get(reference=b.crn)
            if invoice.system == system:
                invoices.append(invoice)
                invoice_list.append(str(b.crn))

    invoice_list = list(set(invoice_list))

    if invoices:
        strIO = StringIO()
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
                    'eftpos': D('0.0'),
                    'cash': D('0.0'),
                    'cheque': D('0.0'),
                    'money_order': D('0.0')
                }
            })
        for d in daterange(banked_start,banked_end):
            banked_dates.append(d.strftime(date_format))
            banked_date_amounts.append({
                'date':d.strftime(date_format),
                'amounts':{
                    'cash': D('0.0'),
                    'cheque': D('0.0'),
                    'money_order': D('0.0')
                }
            })

        dates_row = ''
        for date in dates:
            dates_row += '{},,,'.format(date)

        # Dates row
        writer.writerow(['']+ dates_row.split(','))
        writer.writerow([''] + ['Credit Card','Bpay','EFTPOS'] * len(dates) + ['','Credit Card','Bpay','EFTPOS'])

        # Loop through the payments and not the invoices
        for i in invoices:
            # Add items of invoice if not in list

            if i.order:# and not i.voided:
                lines = i.order.lines.all()
                for x in lines:
                    #print((i, i.__dict__, x, x.oracle_code))
                    item_date_amounts, banked_item_dates_amounts = [], []
                    for d in dates:
                        item_date_amounts.append({
                            'date':d,
                            'amounts':{
                                'card': D('0.0'),
                                'bpay': D('0.0'),
                                'eftpos': D('0.0'),
                                'cash': D('0.0'),
                                'cheque': D('0.0'),
                                'money_order': D('0.0')
                            }
                        })
                    for d in banked_dates:
                        banked_item_dates_amounts.append({
                            'date':d,
                            'amounts':{
                                'cash': D('0.0'),
                                'cheque': D('0.0'),
                                'money_order': D('0.0')
                            }
                        })

                    items.append({
                        'dates':item_date_amounts,
                        'banked_dates': banked_item_dates_amounts,
                        'item': x,
                        'card': D('0.0'),
                        'bpay': D('0.0'),
                        'eftpos': D('0.0'),
                        'cash': D('0.0'),
                        'cheque': D('0.0'),
                        'money_order': D('0.0')
                    })

                    # create empty subtotal list for each oracle code
                    if x.oracle_code not in oracle_codes:
                        oracle_codes[x.oracle_code] = []
                        for d in daterange(start,end):
                            oracle_codes[x.oracle_code].append({
                                'date':d.strftime(date_format),
                                'amounts':{
                                    'card': D('0.0'),
                                    'bpay': D('0.0'),
                                    'eftpos': D('0.0'),
                                    'cash': D('0.0'),
                                    'cheque': D('0.0'),
                                    'money_order': D('0.0')
                                }
                            })

                    if x.oracle_code not in banked_oracle_codes:
                        banked_oracle_codes[x.oracle_code] = []
                        for d in daterange(banked_start,banked_end):
                            banked_oracle_codes[x.oracle_code].append({
                                'date':d.strftime(date_format),
                                'amounts':{
                                    'cash': D('0.0'),
                                    'cheque': D('0.0'),
                                    'money_order': D('0.0')
                                }
                            })

        for item in items:
            price = D(item.get('item').line_price_before_discounts_incl_tax)
            code = item.get('item').oracle_code
            order = item.get('item').order

            payment_details = item.get('item').payment_details
            refund_details = item.get('item').refund_details
            deduction_details = item.get('item').deduction_details

            # Banked Cash
            for d in item['banked_dates']:
                index = 0
                for l in banked_date_amounts:
                    if l.get('date') == d.get('date'):
                        date_amount_index = index
                        break
                    index += 1

                for k,v in payment_details["cash"].items():
                    c = CashTransaction.objects.get(id=int(k))
                    source = c.source
                    if source in set(['cash','cheque','money_order']):
                        if c.created.strftime(date_format) == d.get('date'):
                            banked_oracle_codes[code][date_amount_index]['amounts'][source] += D(v)
                            item[source] += D(v)
                            banked_date_amounts[date_amount_index]['amounts'][source] += D(v)

                for k,v in refund_details["cash"].items():
                    c = CashTransaction.objects.get(id=int(k))
                    source = c.source
                    if source in set(['cash','cheque','money_order']):
                        if c.created.strftime(date_format) == d.get('date'):
                            banked_oracle_codes[code][date_amount_index]['amounts'][source] -= D(v)
                            item[source] -= D(v)
                            banked_date_amounts[date_amount_index]['amounts'][source] -= D(v)

                for k,v in deduction_details["cash"].items():
                    c = CashTransaction.objects.get(id=int(k))
                    source = c.source
                    if source in set(['cash','cheque','money_order']):
                        if c.created.strftime(date_format) == d.get('date'):
                            banked_oracle_codes[code][date_amount_index]['amounts'][source] -= D(v)
                            item[source] -= D(v)
                            banked_date_amounts[date_amount_index]['amounts'][source] -= D(v)


            # Other transactions
            for d in oracle_codes[code]:
                index = 0
                for l in date_amounts:
                    if l.get('date') == d.get('date'):
                        date_amount_index = index
                        break
                    index += 1
                # EFT
                for k,v in payment_details["cash"].items():
                    c = CashTransaction.objects.get(id=int(k))
                    source = c.source
                    if source == 'eftpos':
                        if c.created.strftime(date_format) == d.get('date'):
                            oracle_codes[code][date_amount_index]['amounts']['eftpos'] += D(v)
                            item['eftpos'] += D(v)
                            date_amounts[date_amount_index]['amounts']['eftpos'] += D(v)

                for k,v in refund_details["cash"].items():
                    c = CashTransaction.objects.get(id=int(k))
                    source = c.source
                    if source == 'eftpos':
                        if c.created.strftime(date_format) == d.get('date'):
                            oracle_codes[code][date_amount_index]['amounts']['eftpos'] -= D(v)
                            item['eftpos'] -= D(v)
                            date_amounts[date_amount_index]['amounts']['eftpos'] -= D(v)

                # Card
                for k,v in payment_details['card'].items():
                    c = BpointTransaction.objects.get(id=int(k))
                    if c.settlement_date.strftime(date_format) == d.get('date') and c.approved:
                        oracle_codes[code][date_amount_index]['amounts']['card'] += D(v)
                        item['card'] += D(v)
                        date_amounts[date_amount_index]['amounts']['card'] += D(v)

                for k,v in refund_details['card'].items():
                    c = BpointTransaction.objects.get(id=int(k))
                    if c.settlement_date.strftime(date_format) == d.get('date') and c.approved:
                        oracle_codes[code][date_amount_index]['amounts']['card'] -= D(v)
                        item['card'] -= D(v)
                        date_amounts[date_amount_index]['amounts']['card'] -= D(v)

                # BPAY
                for k,v in payment_details['bpay'].items():
                    b = BpayTransaction.objects.get(id=int(k))
                    if b.approved and b.p_date.strftime(date_format) == d.get('date'):
                        oracle_codes[code][date_amount_index]['amounts']['bpay'] += D(v)
                        item['bpay'] += D(v)
                        date_amounts[date_amount_index]['amounts']['bpay'] += D(v)

                for k,v in refund_details['bpay'].items():
                    b = BpayTransaction.objects.get(id=int(k))
                    if b.approved and b.p_date.strftime(date_format) == d.get('date'):
                        oracle_codes[code][date_amount_index]['amounts']['bpay'] -= D(v)
                        item['bpay'] -= D(v)
                        date_amounts[date_amount_index]['amounts']['bpay'] -= D(v)

        for code in oracle_codes:
            item_str = ''
            item_str += '{},'.format(code)
            card_total = D('0.0')
            bpay_total = D('0.0')
            eftpos_total = D('0.0')
            for d in oracle_codes[code]:
                item_str += '{},{},{},'.format(d['amounts']['card'],d['amounts']['bpay'],d['amounts']['eftpos'])
                card_total += d['amounts']['card']
                bpay_total += d['amounts']['bpay']
                eftpos_total += d['amounts']['eftpos']
            item_str += ',{},{},{},'.format(card_total, bpay_total, eftpos_total)
            if not ((card_total == D('0.0')) and (bpay_total == D('0.0')) and (eftpos_total == D('0.0'))):
                writer.writerow(item_str.split(','))

        total_str = 'Totals,'
        total_amounts = {
            'card': D('0.0'),
            'bpay': D('0.0'),
            'eftpos': D('0.0')
        }
        for d in date_amounts:
            total_amounts['card'] += d['amounts']['card']
            total_amounts['bpay'] += d['amounts']['bpay']
            total_amounts['eftpos'] += d['amounts']['eftpos']
            total_str += '{},{},{},'.format(d['amounts']['card'],d['amounts']['bpay'],d['amounts']['eftpos'])
        total_str += ',{},{},{},'.format(total_amounts['card'],total_amounts['bpay'],total_amounts['eftpos'])
        writer.writerow('')
        writer.writerow(total_str.split(','))

        # Banked Items
        writer.writerow('')
        writer.writerow(fieldnames)
        banked_dates_row = ''
        for date in banked_dates:
            banked_dates_row += '{},,,'.format(date)
        writer.writerow(['']+ banked_dates_row.split(','))
        writer.writerow([''] + ['Cash','Cheque','Money Order'] * len(banked_dates) + ['','Cash','Cheque','Money Order','Banked(Cash,Money Order,Cheque)'])

        for code in banked_oracle_codes:
            banked_item_str = ''
            banked_item_str += '{},'.format(code)
            cash_total = D('0.0')
            cheque_total = D('0.0')
            moneyorder_total = D('0.0')
            for d in banked_oracle_codes[code]:
                banked_item_str += '{},{},{},'.format(d['amounts']['cash'],d['amounts']['cheque'],d['amounts']['money_order'])
                cash_total += d['amounts']['cash']
                cheque_total += d['amounts']['cheque']
                moneyorder_total += d['amounts']['money_order']
            banked_item_str += ',{},{},{},'.format(cash_total, cheque_total, moneyorder_total)
            if not ((cash_total == D('0.0')) and (cheque_total == D('0.0')) and (moneyorder_total == D('0.0'))):
                writer.writerow(banked_item_str.split(','))

        banked_total_str = 'Totals,'
        banked_total_amounts = {
            'cash': D('0.0'),
            'cheque': D('0.0'),
            'money_order': D('0.0')
        }
        for d in banked_date_amounts:
            banked_total_amounts['cash'] += d['amounts']['cash']
            banked_total_amounts['cheque'] += d['amounts']['cheque']
            banked_total_amounts['money_order'] += d['amounts']['money_order']
            banked_total_str += '{},{},{},'.format(d['amounts']['cash'],d['amounts']['cheque'],d['amounts']['money_order'])
        banked_total_str += ',{},{},{},'.format(banked_total_amounts['cash'],banked_total_amounts['cheque'],banked_total_amounts['money_order'])
        writer.writerow('')
        writer.writerow(banked_total_str.split(','))

        strIO.flush()
        strIO.seek(0)
    return strIO

def generate_items_csv_allocated(system,start,end,banked_start,banked_end,region=None,district=None):
    strIO = None
    invoices = []
    invoice_list = []
    dates, banked_dates = [], []
    date_amounts, banked_date_amounts = [], []
    items = []
    oracle_codes = {}
    banked_oracle_codes = {}
    date_format = '%d/%m/%y'

    eftpos = []
    banked_cash = []
    bpoint = []
    bpay = []

#    # Get all transactions
#    if not district:
#        eftpos.extend([x for x in CashTransaction.objects.filter(created__gte=start, created__lte=end, source='eftpos').exclude(district__isnull=False)])
#        banked_cash.extend([x for x in CashTransaction.objects.filter(created__gte=banked_start, created__lte=banked_end).exclude(source='eftpos').exclude(district__isnull=False)])
#        bpoint.extend([x for x in BpointTransaction.objects.filter(settlement_date__gte=start, settlement_date__lte=end).exclude(crn1__endswith='_test')])
#        bpay.extend([x for x in BpayTransaction.objects.filter(p_date__gte=start, p_date__lte=end)])
#    else:
#        eftpos.extend([x for x in CashTransaction.objects.filter(created__gte=start, created__lte=end, source='eftpos',district=district)])
#        banked_cash.extend([x for x in CashTransaction.objects.filter(created__gte=banked_start, created__lte=banked_end,district=district).exclude(source='eftpos')])
#
#    # Get the required invoices
#    for e in eftpos:
#        if e.invoice.reference not in invoice_list:
#            if e.invoice.system == system:
#                invoices.append(e.invoice)
#                invoice_list.append(str(e.invoice.reference))
#    for b in banked_cash:
#        if b.invoice.reference not in invoice_list:
#            if b.invoice.system == system:
#                invoices.append(b.invoice)
#                invoice_list.append(str(b.invoice.reference))
#    for b in bpoint:
#        if b.crn1 not in invoice_list:
#            invoice = Invoice.objects.get(reference=b.crn1)
#            if invoice.system == system:
#                invoices.append(invoice)
#                invoice_list.append(str(b.crn1))
#    for b in bpay:
#        if b.crn not in invoice_list:
#            invoice = Invoice.objects.get(reference=b.crn)
#            if invoice.system == system:
#                invoices.append(invoice)
#                invoice_list.append(str(b.crn))
#
    print (str(banked_start)+ ":"+str(banked_end)+":"+str(system))
    invoices = Invoice.objects.filter(created__gte=banked_start, created__lte=banked_end, system=system)

    print ("INVOICES")
    print (invoices)
    invoice_list = invoices
    invoice_list = list(set(invoice_list))
    if invoices:
        strIO = StringIO()
        fieldnames = ['Account Code', 'Day']
        writer = csv.writer(strIO)
        writer.writerow(fieldnames)

        ########################################################
        ## Header Dates START ##
        ########################################################
        for d in daterange(start,end):
            dates.append(d.strftime(date_format))
            date_amounts.append({
                'date':d.strftime(date_format),
                'amounts':{
                    'card': D('0.0'),
                    'bpay': D('0.0'),
                    'eftpos': D('0.0'),
                    'cash': D('0.0'),
                    'cheque': D('0.0'),
                    'money_order': D('0.0'),
                    'order': D('0.0'), 
                }
            })

        for d in daterange(banked_start,banked_end):
            banked_dates.append(d.strftime(date_format))
            banked_date_amounts.append({
                'date':d.strftime(date_format),
                'amounts':{
                    'cash': D('0.0'),
                    'cheque': D('0.0'),
                    'money_order': D('0.0'),
                    'order': D('0.0'),
                }
            })

        dates_row = ''
        for date in dates:
            dates_row += '{},,,,'.format(date)

        # Dates row
        writer.writerow(['']+ dates_row.split(','))
        writer.writerow([''] + ['Credit Card','Bpay','EFTPOS','Order'] * len(dates) + ['','Credit Card','Bpay','EFTPOS','Order'])
        ########################################################
        #### Header Dates END ####
        ########################################################       

        ####################################################################################################
        ### Oracle Code Grouping Per Day Per Amount START (Electronic Payments, Credit Card,EFTpos Bpay,) ##
        ####################################################################################################

        # Loop through the payments and not the invoices
        for i in invoices:
            # Add items of invoice if not in list
            if i.order:# and not i.voided:
                lines = i.order.lines.all()
                for x in lines:
                    #print((i, i.__dict__, x, x.oracle_code))
                    item_date_amounts, banked_item_dates_amounts = [], []
                    for d in dates:
                        item_date_amounts.append({
                            'date':d,
                            'amounts':{
                                'card': D('0.0'),
                                'bpay': D('0.0'),
                                'eftpos': D('0.0'),
                                'cash': D('0.0'),
                                'cheque': D('0.0'),
                                'money_order': D('0.0'),
                                'order' : D('0.0'),
                            }
                        })

                    for d in banked_dates:
                        banked_item_dates_amounts.append({
                            'date':d,
                            'amounts':{
                                'cash': D('0.0'),
                                'cheque': D('0.0'),
                                'money_order': D('0.0')
                            }
                        })

                    items.append({
                        'dates':item_date_amounts,
                        'banked_dates': banked_item_dates_amounts,
                        'item': x,
                        'card': D('0.0'),
                        'bpay': D('0.0'),
                        'eftpos': D('0.0'),
                        'cash': D('0.0'),
                        'cheque': D('0.0'),
                        'money_order': D('0.0'),
                        'order' : D('0.0'),
                    })

                    
                    # create empty subtotal list for each oracle code
                    if x.oracle_code not in oracle_codes:
                        oracle_codes[x.oracle_code] = []
                        for d in daterange(start,end):
                            oracle_codes[x.oracle_code].append({
                                'date':d.strftime(date_format),
                                'amounts':{
                                    'card': D('0.0'),
                                    'bpay': D('0.0'),
                                    'eftpos': D('0.0'),
                                    'cash': D('0.0'),
                                    'cheque': D('0.0'),
                                    'money_order': D('0.0'),
                                    'order': D('0.0')
                                }
                            })
                    
                    if x.oracle_code not in banked_oracle_codes:
                        banked_oracle_codes[x.oracle_code] = []
                        for d in daterange(banked_start,banked_end):
                            banked_oracle_codes[x.oracle_code].append({
                                'date':d.strftime(date_format),
                                'amounts':{
                                    'cash': D('0.0'),
                                    'cheque': D('0.0'),
                                    'money_order': D('0.0'),
                                    'order' : D('0.0')
                                }
                            })


        for item in items:
            price = D(item.get('item').line_price_before_discounts_incl_tax)
            code = item.get('item').oracle_code
            #order = item.get('item').order
            date_placed = item.get('item').order.date_placed
            payment_details = item.get('item').payment_details
            refund_details = item.get('item').refund_details
            deduction_details = item.get('item').deduction_details

            # Banked Cash
            for d in item['banked_dates']:
                index = 0
                for l in banked_date_amounts:
                    if l.get('date') == d.get('date'):
                        date_amount_index = index
                        break
                    index += 1
                for k,v in payment_details["cash"].items():
                    c = CashTransaction.objects.get(id=int(k))
                    source = c.source
                    if source in set(['cash','cheque','money_order','order']):
                        if c.created.strftime(date_format) == d.get('date'):
                            banked_oracle_codes[code][date_amount_index]['amounts'][source] += D(v)
                            item[source] += D(v)
                            banked_date_amounts[date_amount_index]['amounts'][source] += D(v)

                for k,v in refund_details["cash"].items():
                    c = CashTransaction.objects.get(id=int(k))
                    source = c.source
                    if source in set(['cash','cheque','money_order','order']):
                        if c.created.strftime(date_format) == d.get('date'):
                            banked_oracle_codes[code][date_amount_index]['amounts'][source] -= D(v)
                            item[source] -= D(v)
                            banked_date_amounts[date_amount_index]['amounts'][source] -= D(v)

                for k,v in deduction_details["cash"].items():
                    c = CashTransaction.objects.get(id=int(k))
                    source = c.source
                    if source in set(['cash','cheque','money_order','order']):
                        if c.created.strftime(date_format) == d.get('date'):
                            banked_oracle_codes[code][date_amount_index]['amounts'][source] -= D(v)
                            item[source] -= D(v)
                            banked_date_amounts[date_amount_index]['amounts'][source] -= D(v)

            # Other transactions
            for d in oracle_codes[code]:
                index = 0
                for l in date_amounts:
                    if l.get('date') == d.get('date'):
                        date_amount_index = index
                        break
                    index += 1
                for k,v in payment_details["cash"].items():
                    c = CashTransaction.objects.get(id=int(k))
                    source = c.source
                    if source == 'eftpos':
                        if c.created.strftime(date_format) == d.get('date'):
                            oracle_codes[code][date_amount_index]['amounts']['eftpos'] += D(v)
                            item['eftpos'] += D(v)
                            date_amounts[date_amount_index]['amounts']['eftpos'] += D(v)

                for k,v in refund_details["cash"].items():
                    c = CashTransaction.objects.get(id=int(k))
                    source = c.source
                    if source == 'eftpos':
                        if c.created.strftime(date_format) == d.get('date'):
                            oracle_codes[code][date_amount_index]['amounts']['eftpos'] -= D(v)
                            item['eftpos'] -= D(v)
                            date_amounts[date_amount_index]['amounts']['eftpos'] -= D(v)

#                # Card
#                for k,v in payment_details['card'].items():
#                    c = BpointTransaction.objects.get(id=int(k))
#                    if c.settlement_date.strftime(date_format) == d.get('date') and c.approved:
#                        oracle_codes[code][date_amount_index]['amounts']['card'] += D(v)
#                        item['card'] += D(v)
#                        date_amounts[date_amount_index]['amounts']['card'] += D(v)
#
#                for k,v in refund_details['card'].items():
#                    c = BpointTransaction.objects.get(id=int(k))
#                    if c.settlement_date.strftime(date_format) == d.get('date') and c.approved:
#                        oracle_codes[code][date_amount_index]['amounts']['card'] -= D(v)
#                        item['card'] -= D(v)
#                        date_amounts[date_amount_index]['amounts']['card'] -= D(v)
#
#                # BPAY
#                for k,v in payment_details['bpay'].items():
#                    b = BpayTransaction.objects.get(id=int(k))
#                    if b.approved and b.p_date.strftime(date_format) == d.get('date'):
#                        oracle_codes[code][date_amount_index]['amounts']['bpay'] += D(v)
#                        item['bpay'] += D(v)
#                        date_amounts[date_amount_index]['amounts']['bpay'] += D(v)
#
#                for k,v in refund_details['bpay'].items():
#                    b = BpayTransaction.objects.get(id=int(k))
#                    if b.approved and b.p_date.strftime(date_format) == d.get('date'):
#                        oracle_codes[code][date_amount_index]['amounts']['bpay'] -= D(v)
#                        item['bpay'] -= D(v)
#                        date_amounts[date_amount_index]['amounts']['bpay'] -= D(v)
#

                # Order
                if d.get('date') == date_placed.strftime(date_format):
                    if 'order' in payment_details:
                        print ("ORDER")
                        print (payment_details['order'])
                        for k,v in payment_details['order'].items():
                            #c = BpointTransaction.objects.get(id=int(k))
                            #if c.settlement_date.strftime(date_format) == d.get('date') and c.approved:
                            
                            oracle_codes[code][date_amount_index]['amounts']['order'] += D(v)
                            item['order'] += D(v)
                            date_amounts[date_amount_index]['amounts']['order'] += D(v)
    
                    if 'order' in refund_details: 
                        for k,v in refund_details['order'].items():
                            #c = BpointTransaction.objects.get(id=int(k))
                            #if c.settlement_date.strftime(date_format) == d.get('date') and c.approved:
                            oracle_codes[code][date_amount_index]['amounts']['order'] -= D(v)
                            item['order'] -= D(v)
                            date_amounts[date_amount_index]['amounts']['order'] -= D(v)
    
        for code in oracle_codes:
            item_str = ''
            item_str += '{},'.format(code)
            card_total = D('0.0')
            bpay_total = D('0.0')
            eftpos_total = D('0.0')
            order_total = D('0.0')
            for d in oracle_codes[code]:
                item_str += '{},{},{},{},'.format(d['amounts']['card'],d['amounts']['bpay'],d['amounts']['eftpos'],d['amounts']['order'])
                card_total += d['amounts']['card']
                bpay_total += d['amounts']['bpay']
                eftpos_total += d['amounts']['eftpos']
                order_total += d['amounts']['order']

            item_str += ',{},{},{},{},'.format(card_total, bpay_total, eftpos_total, order_total)
            #if not ((card_total == D('0.0')) and (bpay_total == D('0.0')) and (eftpos_total == D('0.0')) and (order_total == D('0.0'))):
            writer.writerow(item_str.split(','))


        ##################################################################################################
        ### Oracle Code Grouping Per Day Per Amount END (Electronic Payments, Credit Card,EFTpos Bpay,) ## 
        ##################################################################################################


        ##############################################################################################
        ### Oracle Code Grouping Per Day Per Amount END (Manual Payments,  Cash Cheque, Money Order ##
        ##############################################################################################




        total_str = 'Totals,'
        total_amounts = {
            'card': D('0.0'),
            'bpay': D('0.0'),
            'eftpos': D('0.0'),
            'order': D('0.0'),
        }
        for d in date_amounts:
            total_amounts['card'] += d['amounts']['card']
            total_amounts['bpay'] += d['amounts']['bpay']
            total_amounts['eftpos'] += d['amounts']['eftpos']
            total_amounts['order'] += d['amounts']['order']

            total_str += '{},{},{},{},'.format(d['amounts']['card'],d['amounts']['bpay'],d['amounts']['eftpos'],d['amounts']['order'])
        total_str += ',{},{},{},{},'.format(total_amounts['card'],total_amounts['bpay'],total_amounts['eftpos'], total_amounts['order'])
        writer.writerow('')
        writer.writerow(total_str.split(','))
        # Banked Items
        writer.writerow('')
        writer.writerow(fieldnames)
        banked_dates_row = ''
        for date in banked_dates:
            banked_dates_row += '{},,,'.format(date)
        writer.writerow(['']+ banked_dates_row.split(','))
        writer.writerow([''] + ['Cash','Cheque','Money Order'] * len(banked_dates) + ['','Cash','Cheque','Money Order','Banked(Cash,Money Order,Cheque)'])

        for code in banked_oracle_codes:
            banked_item_str = ''
            banked_item_str += '{},'.format(code)
            cash_total = D('0.0')
            cheque_total = D('0.0')
            moneyorder_total = D('0.0')
            order_total = D('0.0')
 
            for d in banked_oracle_codes[code]:
                banked_item_str += '{},{},{},{},'.format(d['amounts']['cash'],d['amounts']['cheque'],d['amounts']['money_order'], d['amounts']['order'])
                cash_total += d['amounts']['cash']
                cheque_total += d['amounts']['cheque']
                moneyorder_total += d['amounts']['money_order']
                order_total +=  d['amounts']['order']
            banked_item_str += ',{},{},{},{},'.format(cash_total, cheque_total, moneyorder_total, order_total)
            if not ((cash_total == D('0.0')) and (cheque_total == D('0.0')) and (moneyorder_total == D('0.0')) and (order_total == D('0.0'))):
                writer.writerow(banked_item_str.split(','))

        banked_total_str = 'Totals,'
        banked_total_amounts = {
            'cash': D('0.0'),
            'cheque': D('0.0'),
            'money_order': D('0.0'),
            'order' : D('0.0'),
        }
        for d in banked_date_amounts:
            banked_total_amounts['cash'] += d['amounts']['cash']
            banked_total_amounts['cheque'] += d['amounts']['cheque']
            banked_total_amounts['money_order'] += d['amounts']['money_order']
            if 'order' in d['amounts']:
                banked_total_amounts['order'] += d['amounts']['order']
            else:
                banked_total_amounts['order'] = D('0.0')
                d['amounts']['order'] = D('0.0')
            banked_total_str += '{},{},{},{},'.format(d['amounts']['cash'],d['amounts']['cheque'],d['amounts']['money_order'],d['amounts']['order'])
        banked_total_str += ',{},{},{},{},'.format(banked_total_amounts['cash'],banked_total_amounts['cheque'],banked_total_amounts['money_order'],banked_total_amounts['order'])
        writer.writerow('')
        writer.writerow(banked_total_str.split(','))

        strIO.flush()
        strIO.seek(0)
    return strIO

def generate_trans_csv(system,start,end,region=None,district=None):
    # Get invoices matching the system and date range
    strIO = None
    invoices = []

    cash = None
    bpoint = None
    bpay = None

    # Get all transactions
    cash = CashTransaction.objects.filter(created__gte=start, created__lte=end,district=district,invoice__system=system).order_by('-created')
    bpoint = BpointTransaction.objects.filter(settlement_date__gte=start, settlement_date__lte=end,crn1__startswith=system).order_by('-created').exclude(crn1__endswith='_test')
    bpay = BpayTransaction.objects.filter(p_date__gte=start, p_date__lte=end,crn__startswith=system).order_by('-created')

    # Print the header
    strIO = StringIO()
    fieldnames = ['Created','Settlement Date', 'Payment Method', 'Transaction Type', 'Amount', 'Approved', 'Source', 'Product Names',
                  'Product Codes', 'Invoice']
    writer = csv.DictWriter(strIO, fieldnames=fieldnames)
    writer.writeheader()

    # Iterate through transactions
    for c in cash:
        i = c.invoice
        items = item_codes = None
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

        
        if c.type not in ['move_in','move_out']:
            cash_info = {
                'Created': c.created.astimezone(PERTH_TIMEZONE).strftime('%d/%m/%Y %H:%M:%S'),
                'Settlement Date': c.created.strftime('%d/%m/%Y'),
                'Invoice': c.invoice.reference,
                'Payment Method': 'Cash',
                'Transaction Type': c.type.lower(),
                'Amount': c.amount if c.type not in ['refund','move_out'] else '-{}'.format(c.amount),
                'Approved': 'True',
                'Source': c.source,
                'Product Names': item_names,
                'Product Codes': oracle_codes
            }
            writer.writerow(cash_info)
    if not district:
        # Write out all bpay transactions
        if bpay:
            for b in bpay:
                i = Invoice.objects.get(reference=b.crn)
                items = item_codes = None
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

                bpay_info = {
                    'Created': b.created.astimezone(PERTH_TIMEZONE).strftime('%d/%m/%Y %H:%M:%S'),
                    'Settlement Date': b.p_date.strftime('%d/%m/%Y'),
                    'Invoice': b.crn,
                    'Payment Method': 'BPAY',
                    'Transaction Type': b.get_p_instruction_code_display(),
                    'Amount': b.amount if b.p_instruction_code == '05' and b.type == '399' else '-{}'.format(b.amount),
                    'Approved': b.approved,
                    'Source': 'N/A',
                    'Product Names': item_names,
                    'Product Codes': oracle_codes
                }
                writer.writerow(bpay_info)
        # Write out all bpoint transactions
        if bpoint:
            for bpt in bpoint:
                i = Invoice.objects.get(reference=bpt.crn1)
                items = item_codes = None
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

                bpoint_info = {
                    'Created': bpt.created.astimezone(PERTH_TIMEZONE).strftime('%d/%m/%Y %H:%M:%S'),
                    'Settlement Date': bpt.settlement_date.strftime('%d/%m/%Y'),
                    'Invoice': bpt.crn1,
                    'Payment Method': 'BPOINT',
                    'Transaction Type': bpt.action.lower(),
                    'Amount': bpt.amount if bpt.action not in ['refund'] else '-{}'.format(bpt.amount),
                    'Approved': bpt.approved,
                    'Source': 'N/A',
                    'Product Names': item_names,
                    'Product Codes': oracle_codes
                }
                writer.writerow(bpoint_info)

    strIO.flush()
    strIO.seek(0)
    return strIO
