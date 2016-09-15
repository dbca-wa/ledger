from ledger.settings_base import *

ROOT_URLCONF = 'parkstay.urls'

INSTALLED_APPS += [
    'parkstay'
]

# maximum number of days allowed for a booking
PS_MAX_BOOKING_LENGTH = 30

WSGI_APPLICATION = 'parkstay.wsgi.application'

TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'parkstay', 'templates'))

STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'parkstay', 'static')))

