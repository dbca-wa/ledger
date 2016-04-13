from confy import env, database
import os

# Project paths
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.join(BASE_DIR, 'ledger')

# Application definitions
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG', False)
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE', False)
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE', False)
if not DEBUG:
    ALLOWED_HOSTS = []  # FIXME in production
ROOT_URLCONF = 'ledger.urls'
ROOT_HOSTCONF = 'ledger.hosts'
DEFAULT_HOST = env('DEFAULT_HOST', 'ledger')
PARENT_HOST = env('PARENT_HOST', 'localhost')
HOST_PORT = env('HOST_PORT', '8000')
WSGI_APPLICATION = 'ledger.wsgi.application'
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social.apps.django_app.default',
    'django_extensions',
    'django_hosts',
    'bootstrap3',
    'reversion',
    'ledger.accounts',   #  Defines custom user model, passwordless auth pipeline.
    'ledger.licence',
    'wildlifelicensing.apps.dashboard',
    'wildlifelicensing.apps.main',
    'wildlifelicensing.apps.applications',
    'wildlifelicensing.apps.emails'
]
SITE_ID = 1
SITE_URL = env('SITE_URL', 'http://localhost:8000')
MIDDLEWARE_CLASSES = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dpaw_utils.middleware.SSOLoginMiddleware',
    'dpaw_utils.middleware.AuditMiddleware',  # Sets model creator/modifier field values.
    'ledger.middleware.FirstTimeNagScreenMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
]

# Authentication settings
LOGIN_URL = '/'
AUTHENTICATION_BACKENDS = (
    'social.backends.email.EmailAuth',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_USER_MODEL = 'accounts.EmailUser'
SOCIAL_AUTH_STRATEGY = 'social.strategies.django_strategy.DjangoStrategy'
SOCIAL_AUTH_STORAGE = 'social.apps.django_app.default.models.DjangoStorage'
SOCIAL_AUTH_EMAIL_FORM_URL = '/ledger/'
SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'ledger.accounts.mail.send_validation'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/ledger/validation-sent/'
SOCIAL_AUTH_PASSWORDLESS = True
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_USERNAME_IS_FULL_EMAIL = True
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['first_name', 'last_name', 'email']
SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.mail.mail_validation',
    'ledger.accounts.pipeline.user_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)

SESSION_COOKIE_DOMAIN = env('SESSION_COOKIE_DOMAIN', None)
if SESSION_COOKIE_DOMAIN:
    SESSION_COOKIE_NAME = (SESSION_COOKIE_DOMAIN + ".ledger_sessionid").replace(".", "_")


# Email settings
ADMINS = ('asi@dpaw.wa.gov.au',)
EMAIL_HOST = env('EMAIL_HOST', 'email.host')
EMAIL_PORT = env('EMAIL_PORT', 25)
EMAIL_FROM = env('EMAIL_FROM', ADMINS[0])
DEFAULT_FROM_EMAIL = EMAIL_FROM


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
            os.path.join(BASE_DIR, 'wildlifelicensing', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


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
LANGUAGE_CODE = 'en-us'
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
    os.path.join(os.path.join(BASE_DIR, 'wildlifelicensing', 'static')),
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
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'ledger.log'),
            'formatter': 'verbose',
            'maxBytes': 5242880
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['file'],
            'level': 'INFO'
        },
        'log': {
            'handlers': ['file'],
            'level': 'INFO'
        },
    }
}
