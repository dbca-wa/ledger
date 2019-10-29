from django.conf import settings


def is_valid_system(system_id):
    ''' Check if the system is in the itsystems register.
    :return: Boolean
    '''
    if settings.VALID_SYSTEMS:
        return system_id in settings.VALID_SYSTEMS
    else:
        logger.warn('VALID_SYSTEMS not set, ledger.payments.helpers.is_valid_system will always return true')
        return True


def belongs_to(user, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """
    return user.groups.filter(name=group_name).exists()


def is_payment_admin(user):
    return user.is_authenticated() and (belongs_to(user, settings.PAYMENT_OFFICERS_GROUP) or user.is_superuser)
