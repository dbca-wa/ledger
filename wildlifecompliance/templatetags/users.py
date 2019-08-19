from django.template import Library
from wildlifecompliance import helpers as wildlifecompliance_helpers

register = Library()


@register.simple_tag(takes_context=True)
def is_customer(context):
    request = context['request']
    return wildlifecompliance_helpers.is_customer(request)

@register.simple_tag(takes_context=True)
def is_officer(context):
    request = context['request']
    return wildlifecompliance_helpers.is_officer(request)

@register.simple_tag(takes_context=True)
def is_wildlifecompliance_admin(context):
    # checks if user is an AdminUser
    request = context['request']
    return wildlifecompliance_helpers.is_wildlifecompliance_admin(request)


@register.simple_tag(takes_context=True)
def is_internal(context):
    # checks if user is a departmentuser and logged in via single sign-on
    request = context['request']
    return wildlifecompliance_helpers.is_internal(request)

@register.simple_tag(takes_context=True)
def is_model_backend(context):
    # Return True if user logged in via single sign-on (or False via
    # social_auth i.e. an external user signing in with a login-token)
    request = context['request']
    return wildlifecompliance_helpers.is_model_backend(request)

@register.simple_tag(takes_context=True)
def is_compliance_internal_user(context):
    request = context['request']
    return wildlifecompliance_helpers.is_compliance_internal_user(request)

@register.simple_tag(takes_context=True)
def prefer_compliance_management(context):
    request = context['request']
    return wildlifecompliance_helpers.prefer_compliance_management(request)

