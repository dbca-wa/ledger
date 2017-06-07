from disturbance.components.organisations.models import Organisation, OrganisationAccessGroup

def can_manage_org(organisation,user):
    try:
        UserDelegation.objects.get(organisation=organisation,user=user)
    except UserDelegation.DoesNotExist:
        return False
    return True
