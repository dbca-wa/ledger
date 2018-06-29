from django.template import Library
#from wildlifelicensing.apps.main import helpers
#from disturbance import helpers
from disturbance import helpers as disturbance_helpers

register = Library()


#@register.filter(name='is_customer')
#def is_customer(user):
#    return helpers.is_customer(user)
#
#@register.filter(name='is_officer')
#def is_officer(user):
#    return helpers.is_officer(user)

@register.simple_tag(takes_context=True)
def is_internal(context):
    # checks if user is (departmentUser or Officer) and logged in via single sign-on
    request = context['request']
    return disturbance_helpers.is_internal(request)


@register.simple_tag(takes_context=True)
def is_model_backend(context):
    # Return True if user logged in via single sign-on (or False via social_auth i.e. an external user signing in with a login-token)
    #import ipdb; ipdb.set_trace()
    request = context['request']
    #return 'ModelBackend' in request.session.get('_auth_user_backend')
    return disturbance_helpers.is_model_backend(request)


