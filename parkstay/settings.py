from ledger.settings_base import *
from decimal import Decimal

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
PS_MAX_BOOKING_LENGTH = 90

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


TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'parkstay', 'templates'))
'''BOOTSTRAP3 = {
    'jquery_url': '//static.dpaw.wa.gov.au/static/libs/jquery/2.2.1/jquery.min.js',
    'base_url': '//static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/',
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
        'LOCATION': os.path.join(BASE_DIR, 'parkstay', 'cache'),
    }
}
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'parkstay', 'static')))
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'parkstay', 'frontend', 'parkstay', 'dist')))


BPAY_ALLOWED = env('BPAY_ALLOWED',False)

OSCAR_BASKET_COOKIE_OPEN = 'parkstay_basket'


CRON_CLASSES = [
    'parkstay.cron.SendBookingsConfirmationCronJob',
    'parkstay.cron.UnpaidBookingsReportCronJob',
]

CAMPGROUNDS_EMAIL = env('CAMPGROUNDS_EMAIL','campgrounds@dpaw.wa.gov.au')
