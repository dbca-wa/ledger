"""
WSGI config for ledger project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
from django.core.wsgi import get_wsgi_application

import confy
confy.read_environment_file("/home/jason/projects/ledger-mooring/.env")
#os.path.join(BASE_PATH, 'staticfiles')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mooring.settings")
application = get_wsgi_application()
