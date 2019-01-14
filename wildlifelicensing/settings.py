from ledger.settings_base import *

ROOT_URLCONF = 'wildlifelicensing.urls'
SITE_ID = 1
INSTALLED_APPS += [
    'bootstrap3',
    'wildlifelicensing.apps.dashboard',
    'wildlifelicensing.apps.main',
    'wildlifelicensing.apps.applications',
    'wildlifelicensing.apps.emails',
    'wildlifelicensing.apps.returns',
    'wildlifelicensing.apps.customer_management',
    'wildlifelicensing.apps.reports',
    'wildlifelicensing.apps.payments'
]

WSGI_APPLICATION = 'wildlifelicensing.wsgi.application'

TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'wildlifelicensing', 'templates'))

BOOTSTRAP3 = {
    'jquery_url': '//static.dpaw.wa.gov.au/static/libs/jquery/2.2.1/jquery.min.js',
    'base_url': '//static.dpaw.wa.gov.au/static/libs/twitter-bootstrap/3.3.6/',
    'css_url': None,
    'theme_url': None,
    'javascript_url': None,
    'javascript_in_head': False,
    'include_jquery': False,
    'required_css_class': 'required-form-field',
    'success_css_class': '',
    'set_placeholder': False,
}

STATICFILES_DIRS.append(os.path.join(os.path.join(BASE_DIR, 'wildlifelicensing', 'static')))

CRON_CLASSES = [
    #'wildlifelicensing.apps.applications.cron.AssessmentRemindersCronJob',
    'wildlifelicensing.apps.main.cron.CheckLicenceRenewalsCronJob',
    'wildlifelicensing.apps.returns.cron.CheckOverdueReturnsCronJob',
]


HERBIE_SPECIES_WFS_URL = env('HERBIE_SPECIES_WFS_URL',
                             'https://kmi.dpaw.wa.gov.au/geoserver/ows?service=wfs&version=1.1.0&'
                             'request=GetFeature&typeNames=public:herbie_hbvspecies_public&outputFormat=application/json')

WL_PAYMENT_SYSTEM_ID = env('WL_PAYMENT_SYSTEM_ID', 'S369')
if not VALID_SYSTEMS:
    VALID_SYSTEMS = [WL_PAYMENT_SYSTEM_ID]
WL_SENIOR_VOUCHER_CODE = env('WL_SENIOR_VOUCHER_CODE', 'WL_SENIOR_VOUCHER')

# next setting is necessary to resolve absolute URL for the emails sent by the tasks running in cron.
DEFAULT_HOST = env('DEFAULT_HOST', "https://wildlifelicensing.dpaw.wa.gov.au")
#set data_upload_max params, otherwise use django default values
DATA_UPLOAD_MAX_NUMBER_FIELDS = env('DATA_UPLOAD_MAX_NUMBER_FIELDS', 1000)
DATA_UPLOAD_MAX_MEMORY_SIZE = env('DATA_UPLOAD_MAX_MEMORY_SIZE', 2621440) #2.5 MB
WL_PDF_URL=env('WL_PDF_URL','https://wildlifelicensing.dpaw.wa.gov.au')
INVOICE_UNPAID_WARNING = env('INVOICE_UNPAID_WARNING', 'Your application cannot be processed until payment is received.')

SYSTEM_NAME = env('SYSTEM_NAME', 'Wildlife Licensing System')
EMAIL_FROM = env('EMAIL_FROM', ADMINS[0])
DEFAULT_FROM_EMAIL = EMAIL_FROM
DEPT_DOMAINS = env('DEPT_DOMAINS', ['dpaw.wa.gov.au', 'dbca.wa.gov.au'])
