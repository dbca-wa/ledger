from django.template import Library
from wildlifelicensing.apps.main import helpers
from mooring import helpers as helper

register = Library()


@register.filter(name='is_customer')
def is_customer(user):
    return helpers.is_customer(user)


@register.filter(name='is_officer')
def is_officer(user):
    return helpers.is_officer(user)

@register.filter(name='is_inventory')
def is_inventory(user):
    return helper.is_inventory(user)

@register.filter(name='is_admin')
def is_admin(user):
    return helper.is_admin(user)