from __future__ import unicode_literals
from ledger.accounts.models import EmailUser


def belongs_to(user, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """
    return user.groups.filter(name=group_name).exists()

def is_model_backend(request):
    # Return True if user logged in via single sign-on (i.e. an internal)
    #import ipdb; ipdb.set_trace()
    return 'ModelBackend' in request.session.get('_auth_user_backend')

def is_email_auth_backend(request):
    # Return True if user logged in via social_auth (i.e. an external user signing in with a login-token)
    #import ipdb; ipdb.set_trace()
    return 'EmailAuth' in request.session.get('_auth_user_backend')

def is_officer(request):
    return request.user.is_authenticated() and is_model_backend(request) and (belongs_to(request.user, 'Disturbance Officers') or request.user.is_superuser)

def in_dbca_domain(request):
    domain = request.user.email.split('@')[1]
    return domain == 'dpaw.wa.gov.au' or domain == 'dbca.wa.gov.au'

def is_departmentUser(request):
    return request.user.is_authenticated() and is_model_backend(request) and in_dbca_domain(request)

def is_customer(request):
    return request.user.is_authenticated() and is_email_auth_backend(request)

def is_internal(request):
    return is_officer(request) or is_departmentUser(request)

def get_all_officers():
    return EmailUser.objects.filter(groups__name='Disturbance Officers')
