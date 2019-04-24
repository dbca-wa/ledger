"""
WSGI config for ledger project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
from django.core.wsgi import get_wsgi_application

import confy
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
confy.read_environment_file(BASE_DIR+"/.env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mooring.settings")
application = get_wsgi_application()
