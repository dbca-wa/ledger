from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from ledger.payments.bpay.crn import test_connection


if not settings.PRODUCTION_EMAIL:
    if not settings.NON_PROD_EMAIL:
        raise ImproperlyConfigured('NON_PROD_EMAIL must not be empty if PRODUCTION_EMAIL is set to False')
    if settings.EMAIL_INSTANCE not in ['PROD','DEV','TEST','UAT']:
        raise ImproperlyConfigured('EMAIL_INSTANCE must be either "PROD","DEV","TEST","UAT"')
    if settings.EMAIL_INSTANCE == 'PROD':
        raise ImproperlyConfigured('EMAIL_INSTANCE cannot be \'PROD\' if PRODUCTION_EMAIL is set to False')

try:
    if not float(settings.LEDGER_GST).is_integer():
        raise ImproperlyConfigured('LEDGER_GST must be an integer')
except Exception as e:
    raise ImproperlyConfigured('LEDGER_GST must be an integer')
if settings.LEDGER_GST < 0 or settings.LEDGER_GST > 99:
    raise ImproperlyConfigured('LEDGER_GST must be between 0 and 100')

# test for BPAY CRN server
if settings.BPAY_GATEWAY:
    test_connection()
