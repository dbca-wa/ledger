from oscar.apps.payment.forms import *
from oscar.core.loading import get_model

Bankcard = get_model('payment','Bankcard')

class BankcardForm(BankcardForm):

    start_month = None
    
    class Meta:
        model = Bankcard
        fields = ('number','expiry_month','ccv')
