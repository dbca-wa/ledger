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
PS_MAX_BOOKING_LENGTH = 90

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
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'parkstay', 'static')))
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'parkstay', 'frontend', 'parkstay', 'dist')))


