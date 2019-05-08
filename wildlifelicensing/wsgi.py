"""
WSGI config for ledger/wildlifelicensing project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import os
import confy
from django.core.wsgi import get_wsgi_application

dot_env = os.path.join(os.getcwd(), '.env')
if os.path.exists(dot_env):
    confy.read_environment_file(".env")   # This line must precede dj_static imports.

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wildlifelicensing.settings")
from dj_static import Cling, MediaCling
application = Cling(MediaCling(get_wsgi_application()))
