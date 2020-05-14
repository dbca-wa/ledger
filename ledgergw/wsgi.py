"""
WSGI config for ledger project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling

import confy
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
confy.read_environment_file(BASE_DIR+"/.env")
print (BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ledgergw.settings")
#application = get_wsgi_application()
application = Cling(MediaCling(get_wsgi_application()))
