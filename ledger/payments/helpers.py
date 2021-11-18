from django.conf import settings
from ledger.payments import models as ledger_payments_models
import logging
logger = logging.getLogger(__name__)

def is_valid_system(system_id):
    ''' Check if the system is in the itsystems register.
    :return: Boolean
    '''
    system_id_zeroed=system_id.replace('S','0')
    ois = ledger_payments_models.OracleInterfaceSystem.objects.filter(system_id=system_id_zeroed,enabled=True, integration_type='bpoint_api')
    if ois.count() > 0:
        return ois[0].system_id
    elif settings.VALID_SYSTEMS:
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
