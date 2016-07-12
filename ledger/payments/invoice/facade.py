from models import Invoice

def create_invoice(order_number,amount):
    '''
        Make a new Invoice object
    '''
    inv = Invoice.objects.create(
        order_number=order_number,
        amount=amount
    )
    return inv