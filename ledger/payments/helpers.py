

def belongs_to(user, group_name):
    """
    Check if the user belongs to the given group.
    :param user:
    :param group_name:
    :return:
    """
    return user.groups.filter(name=group_name).exists()


def is_payment_admin(user):
    return user.is_authenticated() and (belongs_to(user, 'Payments Officers') or user.is_superuser)
