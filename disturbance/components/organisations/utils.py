import string
import random


def can_manage_org(organisation,user):
    from disturbance.components.organisations.models import Organisation, OrganisationAccessGroup
    try:
        UserDelegation.objects.get(organisation=organisation,user=user)
    except UserDelegation.DoesNotExist:
        return False
    return True

def random_generator(size=12, chars=string.letters + string.punctuation + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
