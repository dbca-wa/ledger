from django.conf import settings

BPOINT_CURRENCY = getattr(settings, 'BPOINT_CURRENCY')
BPOINT_BILLER_CODE = getattr(settings, 'BPOINT_BILLER_CODE')
BPOINT_USERNAME = getattr(settings, 'BPOINT_USERNAME')
BPOINT_PASSWORD = getattr(settings,'BPOINT_PASSWORD')
BPOINT_MERCHANT_NUM = getattr(settings,'BPOINT_MERCHANT_NUM')
BPOINT_TEST = getattr(settings, 'BPOINT_TEST') #set transactions to bpoint as test 