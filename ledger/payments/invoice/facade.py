from ledger.payments.invoice.models import Invoice
from ledger.payments.bpay.crn import getCRN, getICRN

def create_invoice_crn(order_number,amount,crn_string,system,text):
    '''Make a new Invoice object using crn
    '''
    inv,created = Invoice.objects.get_or_create(
        order_number=order_number,
        amount=amount,
        reference = getCRN(crn_string)
    )
    if created:
        inv.system = system
        inv.text = text
        inv.save()
    else:
        if inv.system != system:
            inv.system = system
            inv.text = text
            inv.save()
    return inv

def create_invoice_icrn(order_number,amount,crn_string,_format,system,text):
    '''Make a new Invoice object using icrn
    '''
    if _format in ['ICRNDATE','ICRNAMTDATE']:
        if not date:
            raise ValueError('Date is required to generate ICRN number')
    icrn = getICRN(crn_string,amount,_format)
    inv, created = Invoice.objects.get_or_create(
        order_number=order_number,
        amount=amount,
        reference = icrn
    )
    if created:
        inv.system = system
        inv.text = text
        inv.save()
    else:
        if inv.system != system:
            inv.system = system
            inv.text = text
            inv.save()
    return inv
