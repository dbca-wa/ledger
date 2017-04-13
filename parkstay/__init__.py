from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

if not settings.PARK_ENTRY_CODE:
    raise ImproperlyConfigured('PARK_ENTRY_CODE must be set') 
