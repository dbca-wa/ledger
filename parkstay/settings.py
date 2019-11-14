from ledger.settings_base import *


ROOT_URLCONF = 'parkstay.urls'
SITE_ID = 1

# number of seconds before expiring a temporary booking
BOOKING_TIMEOUT = 1200

INSTALLED_APPS += [
    'bootstrap3',
    'parkstay',
    'taggit',
    'rest_framework',
    'rest_framework_gis'
]

MIDDLEWARE_CLASSES += [
    'parkstay.middleware.BookingTimerMiddleware'
]

# maximum number of days allowed for a booking
PS_MAX_BOOKING_LENGTH = 28

# minimum number of remaining campsites to trigger an availaiblity warning
PS_CAMPSITE_COUNT_WARNING = 10

# number of days before clearing un unpaid booking
PS_UNPAID_BOOKING_LAPSE_DAYS = 5

WSGI_APPLICATION = 'parkstay.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'parkstay.perms.OfficerPermission',
    )
}

# disable Django REST Framework UI on prod
if not DEBUG:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']=('rest_framework.renderers.JSONRenderer',)
else:
    REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES']=('rest_framework.renderers.JSONRenderer','rest_framework_csv.renderers.CSVRenderer')


TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'parkstay', 'templates'))
TEMPLATES[0]['OPTIONS']['context_processors'].append('parkstay.context_processors.parkstay_url')
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'parkstay', 'cache'),
    }
}
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'parkstay', 'static')))


BPAY_ALLOWED = env('BPAY_ALLOWED',False)

OSCAR_BASKET_COOKIE_OPEN = 'parkstay_basket'


CRON_CLASSES = [
    #'parkstay.cron.SendBookingsConfirmationCronJob',
    'parkstay.cron.UnpaidBookingsReportCronJob',
    'parkstay.cron.OracleIntegrationCronJob',
]

# Additional logging for parkstay
LOGGING['loggers']['booking_checkout'] = {
    'handlers': ['console'],
    'level': 'INFO'
}

SYSTEM_NAME = env('SYSTEM_NAME', 'Parkstay WA')
EMAIL_FROM = env('EMAIL_FROM', ADMINS[0])
DEFAULT_FROM_EMAIL = EMAIL_FROM
PS_PAYMENT_SYSTEM_ID = env('PS_PAYMENT_SYSTEM_ID', 'S019')
if not VALID_SYSTEMS:
    VALID_SYSTEMS = [PS_PAYMENT_SYSTEM_ID]
EXPLORE_PARKS_URL = env('EXPLORE_PARKS_URL', 'https://parks.dpaw.wa.gov.au')
PARKSTAY_EXTERNAL_URL = env('PARKSTAY_EXTERNAL_URL','https://parkstay.dbca.wa.gov.au')
DEV_STATIC = env('DEV_STATIC',False)
DEV_STATIC_URL = env('DEV_STATIC_URL')
DEPT_DOMAINS = env('DEPT_DOMAINS', ['dpaw.wa.gov.au', 'dbca.wa.gov.au'])
