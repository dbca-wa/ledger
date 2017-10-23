from oscar.apps.payment.forms import *
from oscar.apps.payment.bankcards import VISA,VISA_ELECTRON,MASTERCARD 
from oscar.core.loading import get_model

Bankcard = get_model('payment','Bankcard')

VALID_CARDS = [VISA,VISA_ELECTRON,MASTERCARD]

class BankcardForm(BankcardForm):

    start_month = None
    
    class Meta:
        model = Bankcard
        fields = ('number','expiry_month','ccv')

    @property
    def bankcard(self):
        """
        Return an instance of the Bankcard model (unsaved)
        """
        return Bankcard(number=self.cleaned_data['number'],
                        expiry_date=self.cleaned_data['expiry_month'],
                        ccv=self.cleaned_data['ccv'])
