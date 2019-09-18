from django.core.exceptions import ImproperlyConfigured
from confy import env, database
from oscar.defaults import *
from oscar import get_core_apps, OSCAR_MAIN_TEMPLATE_DIR

import os

# Project paths
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR, 'ledger')

# Application definitions
DEBUG = env('DEBUG', False)
SECRET_KEY = env('SECRET_KEY', 'Placeholder_Secret_Key')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', False)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', False)
if not DEBUG:
    ALLOWED_HOSTS = env('ALLOWED_DOMAINS', '').split(',')
else:
    ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'social_django',
    'django_extensions',
    'reversion',
    'widget_tweaks',
    'django_countries',
    'django_cron',
] + get_core_apps([  # django-oscar overrides
    'ledger.basket',
    'ledger.order',
    'ledger.checkout',
    'ledger.address',
    'ledger.catalogue',
    'ledger.dashboard.catalogue',
    'ledger.payment'
]) + [
    'ledger.accounts',  # Defines custom user model, passwordless auth pipeline.
    'ledger.licence',
    'ledger.payments',
    'ledger.payments.bpay',
    'ledger.payments.bpoint',
    'ledger.payments.cash',
    'ledger.payments.invoice',
    'ledger.taxonomy',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dbca_utils.middleware.SSOLoginMiddleware',
    'dbca_utils.middleware.AuditMiddleware',  # Sets model creator/modifier field values.
    'ledger.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

# Authentication settings
LOGIN_URL = '/'
AUTHENTICATION_BACKENDS = (
    'social_core.backends.email.EmailAuth',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_USER_MODEL = 'accounts.EmailUser'
# for reference, django.conf.settings.X == backend.setting('X')
# this one prevents the email auth backend from creating EmailUsers with a username param
USER_FIELDS = ['email']
SOCIAL_AUTH_STRATEGY = 'social_django.strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social_django.models.DjangoStorage'
SOCIAL_AUTH_EMAIL_FORM_URL = '/ledger/'
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'ledger.accounts.mail.send_validation'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/ledger/validation-sent/'
SOCIAL_AUTH_EMAIL_VALIDATION_ALLOW_REUSE = True
SOCIAL_AUTH_EMAIL_VALIDATION_EXPIRED_THRESHOLD = env('EMAIL_VALIDATION_EXPIRY', 86400)
SOCIAL_AUTH_PASSWORDLESS = True
SOCIAL_AUTH_SESSION_EXPIRATION = env('SESSION_EXPIRATION', False)
SOCIAL_AUTH_MAX_SESSION_LENGTH = env('MAX_SESSION_LENGTH', 1209600)     # two weeks
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['first_name', 'last_name', 'email']
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'ledger.accounts.pipeline.lower_email_address',
    'ledger.accounts.pipeline.logout_previous_session',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'ledger.accounts.pipeline.mail_validation',
    'ledger.accounts.pipeline.user_by_email',
    'social_core.pipeline.user.create_user',
    'ledger.accounts.pipeline.user_is_new_session',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
)

SESSION_COOKIE_DOMAIN = env('SESSION_COOKIE_DOMAIN', None)
if SESSION_COOKIE_DOMAIN:
    SESSION_COOKIE_NAME = (SESSION_COOKIE_DOMAIN + ".ledger_sessionid").replace(".", "_")


# Email settings
ADMINS = ('asi@dbca.wa.gov.au',)
EMAIL_HOST = env('EMAIL_HOST', 'email.host')
EMAIL_PORT = env('EMAIL_PORT', 25)
EMAIL_FROM = env('EMAIL_FROM', ADMINS[0])
DEFAULT_FROM_EMAIL = EMAIL_FROM

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
            OSCAR_MAIN_TEMPLATE_DIR,
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # django-oscar default templates
                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.core.context_processors.metadata',
            ],
        },
    },
]


BOOTSTRAP3 = {
    'jquery_url': '//static.dbca.wa.gov.au/static/libs/jquery/2.2.1/jquery.min.js',
    'base_url': '/static/ledger/',
    'css_url': None,
    'theme_url': None,
    'javascript_url': None,
    'javascript_in_head': False,
    'include_jquery': False,
    'required_css_class': 'required-form-field',
    'set_placeholder': False,
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}


# Database
DATABASES = {
    # Defined in the DATABASE_URL env variable.
    'default': database.config(),
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-AU'
TIME_ZONE = 'Australia/Perth'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(os.path.join(BASE_DIR, 'ledger', 'static')),
# Removed as these should be in the individual app settings.py and not in ledger.
# leaving hashed in case issues are caused by this.
#    os.path.join(os.path.join(BASE_DIR, 'wildlifelicensing', 'static')),
#    os.path.join(os.path.join(BASE_DIR, 'wildlifecompliance', 'static')),
]
if not os.path.exists(os.path.join(BASE_DIR, 'media')):
    os.mkdir(os.path.join(BASE_DIR, 'media'))
MEDIA_ROOT = env('MEDIA_ROOT', os.path.join(BASE_DIR, 'media'))
MEDIA_URL = '/media/'

# Logging settings
# Ensure that the logs directory exists:
if not os.path.exists(os.path.join(BASE_DIR, 'logs')):
    os.mkdir(os.path.join(BASE_DIR, 'logs'))
LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': env('LOG_CONSOLE_LEVEL', 'INFO'),
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('LOG_CONSOLE_LEVEL', 'WARNING'),
            'propagate': False
        },
        'log': {
            'handlers': ['console'],
            'level': 'INFO'
        },
    }
}

# django-dynamic-fields test generation settings
DDF_FILL_NULLABLE_FIELDS = False

# Ledger settings
CMS_URL=env('CMS_URL',None)
VALID_SYSTEMS=env('VALID_SYSTEMS', '')
VALID_SYSTEMS=VALID_SYSTEMS.split(',') if VALID_SYSTEMS else []
LEDGER_USER=env('LEDGER_USER',None)
LEDGER_PASS=env('LEDGER_PASS')
NOTIFICATION_EMAIL=env('NOTIFICATION_EMAIL')
BPAY_GATEWAY = env('BPAY_GATEWAY', None)
INVOICE_UNPAID_WARNING = env('INVOICE_UNPAID_WARNING', '')
# GST Settings
LEDGER_GST = env('LEDGER_GST',10)
# BPAY settings
BPAY_ALLOWED = env('BPAY_ALLOWED',True)
BPAY_BILLER_CODE=env('BPAY_BILLER_CODE')
# BPOINT settings
BPOINT_CURRENCY='AUD'
BPOINT_BILLER_CODE=env('BPOINT_BILLER_CODE')
BPOINT_USERNAME=env('BPOINT_USERNAME')
BPOINT_PASSWORD=env('BPOINT_PASSWORD')
BPOINT_MERCHANT_NUM=env('BPOINT_MERCHANT_NUM')
BPOINT_TEST=env('BPOINT_TEST',True)
# Custom Email Settings
EMAIL_BACKEND = 'ledger.ledger_email.LedgerEmailBackend'
PRODUCTION_EMAIL = env('PRODUCTION_EMAIL', False)
# Intercept and forward email recipient for non-production instances
# Send to list of NON_PROD_EMAIL users instead
EMAIL_INSTANCE = env('EMAIL_INSTANCE', 'DEV')
NON_PROD_EMAIL = env('NON_PROD_EMAIL', 'noreply@dbca.wa.gov.au')
if not PRODUCTION_EMAIL:
    if not NON_PROD_EMAIL:
        raise ImproperlyConfigured('NON_PROD_EMAIL must not be empty if PRODUCTION_EMAIL is set to False')
    if EMAIL_INSTANCE not in ['PROD', 'DEV', 'TEST', 'UAT']:
        raise ImproperlyConfigured('EMAIL_INSTANCE must be either "PROD","DEV","TEST","UAT"')
    if EMAIL_INSTANCE == 'PROD':
        raise ImproperlyConfigured('EMAIL_INSTANCE cannot be \'PROD\' if PRODUCTION_EMAIL is set to False')

# Oscar settings
OSCAR_ALLOW_ANON_CHECKOUT = True
OSCAR_SHOP_NAME = env('OSCAR_SHOP_NAME')
OSCAR_DASHBOARD_NAVIGATION.append(
    {
        'label': 'Payments',
        'icon': 'icon-globe',
        'children': [
            {
                'label': 'Invoices',
                'url_name': 'payments:invoices-list',
            },
            {
                'label': 'BPAY collections',
                'url_name': 'payments:bpay-collection-list',
            },
            {
                'label': 'BPOINT transactions',
                'url_name': 'payments:bpoint-dash-list',
            },
        ]
    }
)
OSCAR_DEFAULT_CURRENCY = 'AUD'
ORACLE_IMPORT_SEQUENCE = env('ORACLE_IMPORT_SEQUENCE', 70000)
