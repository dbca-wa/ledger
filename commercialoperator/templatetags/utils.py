from django.template import Library
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

register = Library()


@register.simple_tag()
def system_name():
    return settings.SYSTEM_NAME

@register.simple_tag()
def system_name_short():
    return settings.SYSTEM_NAME_SHORT

@register.simple_tag()
def support_email():
    return settings.SUPPORT_EMAIL

@register.simple_tag()
def dept_name():
    return settings.DEP_NAME

@register.simple_tag()
def dept_support_phone():
    return settings.DEP_PHONE_SUPPORT

@register.simple_tag()
def can_show_tests():
    return settings.SHOW_TESTS_URL

