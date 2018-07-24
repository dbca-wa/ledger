from django.core.exceptions import ImproperlyConfigured
from ledger.settings_base import *

ROOT_URLCONF = 'disturbance.urls'
SITE_ID = 1
DEPT_DOMAINS = env('DEPT_DOMAINS', ['dpaw.wa.gov.au', 'dbca.wa.gov.au'])

INSTALLED_APPS += [
    'bootstrap3',
    'disturbance',
    'disturbance.components.main',
    'disturbance.components.organisations',
    'disturbance.components.users',
    'disturbance.components.proposals',
    'disturbance.components.approvals',
    'disturbance.components.compliances',
    'taggit',
    'rest_framework',
    'rest_framework_gis',
    'reset_migrations',
    'ckeditor',
]

# maximum number of days allowed for a booking
WSGI_APPLICATION = 'disturbance.wsgi.application'

'''REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'disturbance.perms.OfficerPermission',
    )
}'''

#REST_FRAMEWORK = {
#    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
#        'PAGE_SIZE': 3
#}

MIDDLEWARE_CLASSES += [
    'disturbance.middleware.FirstTimeNagScreenMiddleware'
]

TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'disturbance', 'templates'))
TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'disturbance','components','organisations', 'templates'))
TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'disturbance','components','emails', 'templates'))
BOOTSTRAP3 = {
    'jquery_url': '//static.dpaw.wa.gov.au/static/libs/jquery/2.2.1/jquery.min.js',
    'base_url': '//static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/',
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
        'LOCATION': os.path.join(BASE_DIR, 'disturbance', 'cache'),
    }
}
STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'disturbance', 'static')))
DEV_STATIC = env('DEV_STATIC',False)
DEV_STATIC_URL = env('DEV_STATIC_URL')
if DEV_STATIC and not DEV_STATIC_URL:
    raise ImproperlyConfigured('If running in DEV_STATIC, DEV_STATIC_URL has to be set')
DATA_UPLOAD_MAX_NUMBER_FIELDS = None

# Department details
VIA_EMAIL = env('VIA_EMAIL','via@dbca.wa.gov.au')
DEP_URL = env('DEP_URL','www.dbca.wa.gov.au')
DEP_PHONE = env('DEP_PHONE','(08) 9219 9831')
DEP_FAX = env('DEP_FAX','(08) 9423 8242')
DEP_POSTAL = env('DEP_POSTAL','Locked Bag 104, Bentley Delivery Centre, Western Australia 6983')
DEP_NAME = env('DEP_NAME','Department of Biodiversity,Conservation and Attractions')
SITE_URL = env('SITE_URL','https://via-uat.dpaw.wa.gov.au')
TENURE_SECTION = env('TENURE_SECTION', None)

BASE_URL=env('BASE_URL')

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        #'width': 300,
        'width': '100%',
    },
    'awesome_ckeditor': {
        'toolbar': 'Basic',
    },
}

