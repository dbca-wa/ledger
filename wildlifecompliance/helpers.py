from __future__ import unicode_literals
from ledger.accounts.models import EmailUser
from wildlifecompliance import settings
from wildlifecompliance.components.applications.models import ActivityPermissionGroup


def belongs_to(user, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """
    return user.groups.filter(name=group_name).exists()


def belongs_to_list(user, group_names):
    """
    Check if the user belongs to the given list of groups.
    :param user:
    :param list_of_group_names:
    :return:
    """
    return user.groups.filter(name__in=group_names).exists()


def is_model_backend(request):
    # Return True if user logged in via single sign-on (i.e. an internal)
    return 'ModelBackend' in request.session.get('_auth_user_backend')


def is_email_auth_backend(request):
    # Return True if user logged in via social_auth (i.e. an external user
    # signing in with a login-token)
    return 'EmailAuth' in request.session.get('_auth_user_backend')


def is_wildlifecompliance_admin(request):
    return request.user.is_authenticated() and is_model_backend(request) and in_dbca_domain(
        request) and (request.user.has_perm('wildlifecompliance.system_administrator') or request.user.is_superuser)


def in_dbca_domain(request):
    user = request.user
    domain = user.email.split('@')[1]
    if domain in settings.DEPT_DOMAINS:
        if not user.is_staff:
            # hack to reset department user to is_staff==True, if the user
            # logged in externally (external departmentUser login defaults to
            # is_staff=False)
            user.is_staff = True
            user.save()
        return True
    return False


def is_departmentUser(request):
    return request.user.is_authenticated() and (is_model_backend(
        request) or settings.ALLOW_EMAIL_ADMINS) and in_dbca_domain(request)


def is_customer(request):
    return request.user.is_authenticated() and is_email_auth_backend(request)


def is_internal(request):
    return is_departmentUser(request)


def is_officer(request):
    licence_officer_groups = [group.name for group in ActivityPermissionGroup.objects.filter(
            permissions__codename__in=['read_only',
                                       'organisation_access_request',
                                       'licensing_officer',
                                       'issuing_officer',
                                       'assessor',
                                       'return_curator',
                                       'payment_officer'])]
    return request.user.is_authenticated() and (belongs_to_list(
        request.user, licence_officer_groups) or request.user.is_superuser)


def get_all_officers():
    licence_officer_groups = ActivityPermissionGroup.objects.filter(
            permissions__codename__in=['read_only',
                                       'organisation_access_request',
                                       'licensing_officer',
                                       'issuing_officer',
                                       'assessor',
                                       'return_curator',
                                       'payment_officer'])
    return EmailUser.objects.filter(
        groups__name__in=licence_officer_groups)
