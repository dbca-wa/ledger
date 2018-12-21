from ledger.settings_base import *
from decimal import Decimal

ROOT_URLCONF = 'mooring.urls'
SITE_ID = 1

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_mo')

# number of seconds before expiring a temporary booking
BOOKING_TIMEOUT = 1200

INSTALLED_APPS += [
    'bootstrap3',
    'mooring',
    'taggit',
    'rest_framework',
    'rest_framework_gis'
]

MIDDLEWARE_CLASSES += [
    'mooring.middleware.BookingTimerMiddleware'
]

# maximum number of days allowed for a booking
PS_MAX_BOOKING_LENGTH = 28

# minimum number of remaining campsites to trigger an availaiblity warning
PS_CAMPSITE_COUNT_WARNING = 10

# number of days before clearing un unpaid booking
PS_UNPAID_BOOKING_LAPSE_DAYS = 5

WSGI_APPLICATION = 'mooring.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'mooring.perms.OfficerPermission',
    )
}

# disable Django REST Framework UI on prod
if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']=('rest_framework.renderers.JSONRenderer',)
else:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']=('rest_framework.renderers.JSONRenderer','rest_framework_csv.renderers.CSVRenderer')


TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'mooring', 'templates'))
TEMPLATES[0]['OPTIONS']['context_processors'].append('mooring.context_processors.mooring_url')
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
        'LOCATION': os.path.join(BASE_DIR, 'mooring', 'cache'),
    }
}
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'mooring', 'static')))


BPAY_ALLOWED = env('BPAY_ALLOWED',False)

OSCAR_BASKET_COOKIE_OPEN = 'mooring_basket'


CRON_CLASSES = [
    #'mooring.cron.SendBookingsConfirmationCronJob',
    'mooring.cron.UnpaidBookingsReportCronJob',
    'mooring.cron.OracleIntegrationCronJob',
]

# Additional logging for mooring
LOGGING['handlers']['booking_checkout'] = {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'mooring_booking_checkout.log'),
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

SYSTEM_NAME = env('SYSTEM_NAME', 'Mooring Rental System')
SYSTEM_NAME_SHORT = env('SYSTEM_NAME_SHORT', 'mooring')
CAMPGROUNDS_EMAIL = env('CAMPGROUNDS_EMAIL','mooringbookings@dbca.wa.gov.au')
DEFAULT_FROM_EMAIL = env('EMAIL_FROM','no-reply@dbca.wa.gov.au')
EXPLORE_PARKS_URL = env('EXPLORE_PARKS_URL','https://mooring.dbca.wa.gov.au/')
PARKSTAY_EXTERNAL_URL = env('PARKSTAY_EXTERNAL_URL','https://mooring.dbca.wa.gov.au/')
DEV_STATIC = env('DEV_STATIC',False)
DEV_STATIC_URL = env('DEV_STATIC_URL')
ROTTNEST_ISLAND_URL = env('ROTTNEST_URL', [])
DEPT_DOMAINS = env('DEPT_DOMAINS', ['dpaw.wa.gov.au', 'dbca.wa.gov.au'])
