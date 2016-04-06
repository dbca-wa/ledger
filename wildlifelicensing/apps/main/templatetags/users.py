from django.template import Library
from wildlifelicensing.apps.main import helpers

register = Library()


@register.filter(name='is_officer')
def is_officer(user):
    return helpers.is_officer(user)
