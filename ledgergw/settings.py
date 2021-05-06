from ledger.settings_base import *
from decimal import Decimal
import os

ROOT_URLCONF = 'ledgergw.urls'
SITE_ID = 1
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_ledger')

# number of seconds before expiring a temporary booking
BOOKING_TIMEOUT = 1200

INSTALLED_APPS += [
    'bootstrap3',
    'taggit',
    'rest_framework',
    'rest_framework_gis',
    'crispy_forms',
    'ledgergw',
    'webtemplate_dbca'
]

MIDDLEWARE_CLASSES += [
]

# maximum number of days allowed for a booking
PS_MAX_BOOKING_LENGTH = 28

# minimum number of remaining campsites to trigger an availaiblity warning
PS_CAMPSITE_COUNT_WARNING = 10

# number of days before clearing un unpaid booking
PS_UNPAID_BOOKING_LAPSE_DAYS = 5

WSGI_APPLICATION = 'ledgergw.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
    )
}

# disable Django REST Framework UI on prod
if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']=('rest_framework.renderers.JSONRenderer',)
else:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']=('rest_framework.renderers.JSONRenderer','rest_framework_csv.renderers.CSVRenderer')


TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'ledgergw', 'templates'))
#TEMPLATES[0]['OPTIONS']['context_processors'].append('ledgergw.context_processors.ledgergw_url')
'''BOOTSTRAP3 = {
    'jquery_url': '/static/common/css/jquery.min.js',
    'base_url': '/static/common/css//twitter-bootstrap/3.3.6/',
    'css_url': None,
    'theme_url': None,
    'javascript_url': None,
    'javascript_in_head': False,
    'include_jquery': False,
    'required_css_class': 'required-form-field',
    'set_placeholder': False,
}'''
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'ledgergw', 'cache'),
    }
}
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'ledgergw', 'static')))


BPAY_ALLOWED = env('BPAY_ALLOWED',False)
OSCAR_BASKET_COOKIE_OPEN = 'ledgergw_basket'

CRON_CLASSES = [
]

# Additional logging
LOGGING['handlers']['booking_checkout'] = {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'ledger_booking_checkout.log'),
            'formatter': 'verbose',
            'maxBytes': 5242880
        }
LOGGING['loggers']['booking_checkout'] = {
            'handlers': ['booking_checkout'],
            'level': 'INFO'
        }

#PS_PAYMENT_SYSTEM_ID = env('PS_PAYMENT_SYSTEM_ID', 'S019')
PS_PAYMENT_SYSTEM_ID = env('PS_PAYMENT_SYSTEM_ID', 'S516')
if not VALID_SYSTEMS:
    VALID_SYSTEMS = [PS_PAYMENT_SYSTEM_ID]

SYSTEM_NAME = env('SYSTEM_NAME', 'Ledger GW')
SYSTEM_NAME_SHORT = env('SYSTEM_NAME_SHORT', 'ledgergw')
CAMPGROUNDS_EMAIL = env('CAMPGROUNDS_EMAIL','asi@dbca.wa.gov.au')
ROTTNEST_EMAIL = env('ROTTNEST_EMAIL', 'asi@dbca.wa.gov.au')
DEFAULT_FROM_EMAIL = env('EMAIL_FROM','no-reply@dbca.wa.gov.au')
EXPLORE_PARKS_URL = env('EXPLORE_PARKS_URL','https://mooring.dbca.wa.gov.au/')
PARKSTAY_EXTERNAL_URL = env('PARKSTAY_EXTERNAL_URL','https://mooring.dbca.wa.gov.au/')
DEV_STATIC = env('DEV_STATIC',False)
DEV_STATIC_URL = env('DEV_STATIC_URL')
ROTTNEST_ISLAND_URL = env('ROTTNEST_URL', [])
DEPT_DOMAINS = env('DEPT_DOMAINS', ['dpaw.wa.gov.au', 'dbca.wa.gov.au'])
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Use git commit hash for purging cache in browser for deployment changes
GIT_COMMIT_HASH = ''
GIT_COMMIT_DATE = ''
if  os.path.isdir(BASE_DIR+'/.git/') is True:
    GIT_COMMIT_DATE = os.popen('cd '+BASE_DIR+' ; git log -1 --format=%cd').read()
    GIT_COMMIT_HASH = os.popen('cd  '+BASE_DIR+' ; git log -1 --format=%H').read()
if len(GIT_COMMIT_HASH) == 0: 
    GIT_COMMIT_HASH = os.popen('cat /app/git_hash').read()
    if len(GIT_COMMIT_HASH) == 0:
       print ("ERROR: No git hash provided")
VERSION_NO = '2.04'
#os.environ['UPDATE_PAYMENT_ALLOCATION'] = 'True'
UNALLOCATED_ORACLE_CODE = 'NNP449 GST' 

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240 
# allow upload big file
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 50  # 15M
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE

#os.environ.setdefault("UPDATE_PAYMENT_ALLOCATION", True)
