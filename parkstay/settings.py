from ledger.settings_base import *

ROOT_URLCONF = 'parkstay.urls'

INSTALLED_APPS += [
    'parkstay'
]

WSGI_APPLICATION = 'parkstay.wsgi.application'

TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'parkstay', 'templates'))

STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'parkstay', 'static')))

