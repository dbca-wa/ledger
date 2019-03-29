from django.core.exceptions import ImproperlyConfigured
from ledger.settings_base import *

ROOT_URLCONF = 'wildlifecompliance.urls'
SITE_ID = 1

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_wc')

INSTALLED_APPS += [
    'django.contrib.humanize',
    'bootstrap3',
    'wildlifecompliance',
    'wildlifecompliance.components.main',
    'wildlifecompliance.components.applications',
    'wildlifecompliance.components.organisations',
    'wildlifecompliance.components.licences',
    'wildlifecompliance.components.users',
    'wildlifecompliance.components.returns',
    'wildlifecompliance.components.call_email',
    'taggit',
    'rest_framework',
    'rest_framework_gis'
]

# maximum number of days allowed for a booking
WSGI_APPLICATION = 'wildlifecompliance.wsgi.application'

'''REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'wildlifecompliance.perms.OfficerPermission',
    )
}'''

MIDDLEWARE_CLASSES += [
    'wildlifecompliance.middleware.FirstTimeNagScreenMiddleware'
]

LATEX_GRAPHIC_FOLDER = os.path.join(BASE_DIR,"templates","latex","images")

TEMPLATES[0]['DIRS'].append(
    os.path.join(
        BASE_DIR,
        'wildlifecompliance',
        'templates'))
TEMPLATES[0]['DIRS'].append(
    os.path.join(
        BASE_DIR,
        'wildlifecompliance',
        'components',
        'organisations',
        'templates'))
TEMPLATES[0]['DIRS'].append(
    os.path.join(
        BASE_DIR,
        'wildlifecompliance',
        'components',
        'emails',
        'templates'))
BOOTSTRAP3 = {
    'jquery_url': '//static.dbca.wa.gov.au/static/libs/jquery/2.2.1/jquery.min.js',
    'base_url': '//static.dbca.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/',
    'css_url': None,
    'theme_url': None,
    'javascript_url': None,
    'javascript_in_head': False,
    'include_jquery': False,
    'required_css_class': 'required-form-field',
    'set_placeholder': False,
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(BASE_DIR, 'wildlifecompliance', 'cache'),
    }
}

# Additional logging for wildlifecompliance
LOGGING['handlers']['application_checkout'] = {
    'level': 'INFO',
    'class': 'logging.handlers.RotatingFileHandler',
    'filename': os.path.join(
        BASE_DIR,
        'logs',
        'wildlifecompliance_application_checkout.log'),
    'formatter': 'verbose',
    'maxBytes': 5242880}
LOGGING['loggers']['application_checkout'] = {
    'handlers': ['application_checkout'],
    'level': 'INFO'
}

STATICFILES_DIRS.append(
    os.path.join(
        os.path.join(
            BASE_DIR,
            'wildlifecompliance',
            'static')))
DEV_STATIC = env('DEV_STATIC', False)
DEV_STATIC_URL = env('DEV_STATIC_URL')
DEV_APP_BUILD_URL = env('DEV_APP_BUILD_URL')  # URL of the Dev app.js served by webpack & express
if DEV_STATIC and not DEV_STATIC_URL:
    raise ImproperlyConfigured(
        'If running in DEV_STATIC, DEV_STATIC_URL has to be set')
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Department details
SYSTEM_NAME = env('SYSTEM_NAME', 'Wildlife Licensing System')
SYSTEM_EMAIL = env('SYSTEM_EMAIL', 'wildlifelicensing@dbca.wa.gov.au')
WC_PAYMENT_SYSTEM_ID = env('WC_PAYMENT_SYSTEM_ID', 'S999')
if not VALID_SYSTEMS:
    VALID_SYSTEMS = [WC_PAYMENT_SYSTEM_ID]
DEP_URL = env('DEP_URL', 'www.dbca.wa.gov.au')
DEP_PHONE = env('DEP_PHONE', '(08) 9219 9831')
DEP_FAX = env('DEP_FAX', '(08) 9423 8242')
DEP_POSTAL = env(
    'DEP_POSTAL',
    'Locked Bag 104, Bentley Delivery Centre, Western Australia 6983')
DEP_NAME = env(
    'DEP_NAME',
    'Department of Biodiversity, Conservation and Attractions')
DEPT_DOMAINS = env('DEPT_DOMAINS', ['dpaw.wa.gov.au', 'dbca.wa.gov.au'])
SITE_PREFIX = env('SITE_PREFIX')
SITE_DOMAIN = env('SITE_DOMAIN')
GROUP_PREFIX = env('GROUP_PREFIX', 'Wildlife Compliance')
SITE_URL = env('SITE_URL', 'https://' + SITE_PREFIX + '.' + SITE_DOMAIN)
EXT_USER_API_ROOT_URL = env('EXT_USER_API_ROOT_URL', None)
EXCEL_OUTPUT_PATH = env('EXCEL_OUTPUT_PATH')
ALLOW_EMAIL_ADMINS = env('ALLOW_EMAIL_ADMINS', False)  # Allows internal pages to be accessed via email authentication
SYSTEM_APP_LABEL = env('SYSTEM_APP_LABEL', 'wildlifecompliance')  # global app_label for group permissions filtering
