import os

from ledger.settings import *

ROOT_URLCONF = 'wildlifelicensing.urls'

INSTALLED_APPS += [
    'compressor',
    'bootstrap3',
    'require',
]

PROJECT_APPS = [
    'wildlifelicensing.apps.accounts',
    'wildlifelicensing.apps.applicants',
    'wildlifelicensing.apps.officers',
]

INSTALLED_APPS = PROJECT_APPS + INSTALLED_APPS

TEMPLATES[0]['DIRS'] = [os.path.join(BASE_DIR, 'wildlifelicensing', 'templates')]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

COMPRESS_PRECOMPILERS = (
    ('text/less', 'lessc {infile} {outfile}'),
)

STATICFILES_STORAGE = 'require.storage.OptimizedStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(os.path.join(BASE_DIR, 'wildlifelicensing', 'static')),
]

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'

EMAIL_HOST = 'alerts.corporateict.domain'
EMAIL_PORT = 25


# The baseUrl to pass to the r.js optimizer, relative to STATIC_ROOT.
REQUIRE_BASE_URL = "js"

# The name of a build profile to use for your project, relative to REQUIRE_BASE_URL.
# A sensible value would be 'app.build.js'. Leave blank to use the built-in default build profile.
# Set to False to disable running the default profile (e.g. if only using it to build Standalone
# Modules)
REQUIRE_BUILD_PROFILE = 'app.build.js'

# The name of the require.js script used by your project, relative to REQUIRE_BASE_URL.
REQUIRE_JS = "require.js"

# A dictionary of standalone modules to build with almond.js.
# See the section on Standalone Modules, below.
REQUIRE_STANDALONE_MODULES = {}

# Whether to run django-require in debug mode.
REQUIRE_DEBUG = DEBUG

# A tuple of files to exclude from the compilation result of r.js.
REQUIRE_EXCLUDE = ("build.txt",)

# The execution environment in which to run r.js: auto, node or rhino.
# auto will auto-detect the environment and make use of node if available and rhino if not.
# It can also be a path to a custom class that subclasses
# require.environments.Environment and defines some "args" function that
# returns a list with the command arguments to execute.
REQUIRE_ENVIRONMENT = "auto"
