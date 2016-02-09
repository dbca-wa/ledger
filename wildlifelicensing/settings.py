import os

from ledger.settings import *


INSTALLED_APPS += [
                   'compressor',
                   'bootstrap3',
                   ]

TEMPLATES[0]['DIRS'].append(os.path.join(BASE_DIR, 'wildlifelicensing', 'templates'))

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
)

STATICFILES_DIRS = [
    os.path.join(os.path.join(BASE_DIR, 'wildlifelicensing', 'static')),
]
