from ledger.payments.invoice.models import Invoice
from ledger.payments.bpay.crn import getCRN, getICRN


def _get_payment_choice(payment_method):
    if payment_method == 'card':
        return Invoice.PAYMENT_METHOD_CC
    elif payment_method == 'bpay':
        return Invoice.PAYMENT_METHOD_BPAY
    elif payment_method == 'monthly_invoicing':
        return Invoice.PAYMENT_METHOD_MONTHLY_INVOICING
    elif payment_method == 'other':
        return Invoice.PAYMENT_METHOD_OTHER
    return None

def create_invoice_crn(order_number, amount, crn_string, system, text, payment_method=None, invoice_name='', due_date=None):
    '''Make a new Invoice object using crn
    '''

    inv_lookup = Invoice.objects.filter(order_number=order_number)
    if inv_lookup.count() > 0:
        inv = Invoice.objects.get(order_number=order_number)        
        created = inv.created
    else:
        Invoice.objects.create(
            order_number=order_number,
            amount=amount,
            reference = getCRN(crn_string),
            invoice_name=invoice_name,
            due_date=due_date
        )
        inv = Invoice.objects.get(order_number=order_number)  
        created = inv.created
    
    if created:
        if payment_method:
            inv.payment_method = _get_payment_choice(payment_method)
        inv.system = system
        inv.text = text
        inv.save()
    else:
        if inv.system != system:
            inv.system = system
            inv.text = text
            inv.save()
    return inv

def create_invoice_icrn(order_number, amount, crn_string, _format, system, text, payment_method=None, invoice_name='', due_date=None):
    '''Make a new Invoice object using icrn
    '''
    if _format in ['ICRNDATE','ICRNAMTDATE']:
        if not date:
            raise ValueError('Date is required to generate ICRN number')
    icrn = getICRN(crn_string,amount,_format)


    inv_lookup = Invoice.objects.filter(order_number=order_number)
    if inv_lookup.count() > 0:
        inv = Invoice.objects.get(order_number=order_number)   
        created = inv.created     
    else:
        Invoice.objects.create(
            order_number=order_number,
            amount=amount,
            reference = icrn,
            invoice_name=invoice_name,
            due_date=due_date  
        )
        inv = Invoice.objects.get(order_number=order_number)  
        created = inv.created

    if created:
        if payment_method:
            inv.payment_method = _get_payment_choice(payment_method)
        inv.system = system
        inv.text = text
        inv.save()
    else:
        if inv.system != system:
            inv.system = system
            inv.text = text
            inv.save()
    return inv
