import string
import random


def can_manage_org(organisation,user):
    from commercialoperator.components.organisations.models import Organisation, OrganisationAccessGroup,UserDelegation
    from ledger.accounts.models import EmailUser
    try:
        UserDelegation.objects.get(organisation=organisation,user=user)
        return True
    except UserDelegation.DoesNotExist:
        pass
    try:
        group = OrganisationAccessGroup.objects.first()
        if group:
            group.members.get(id=user.id)
        return True
    except EmailUser.DoesNotExist:
        pass
    if user.is_superuser:
        return True 
    return False

def can_admin_org(organisation,user):
    from commercialoperator.components.organisations.models import Organisation, OrganisationAccessGroup,UserDelegation,OrganisationContact
    from ledger.accounts.models import EmailUser
    try:
        org_contact=OrganisationContact.objects.get(organisation_id=organisation,email=user.email)
        # if org_contact.can_edit

        return org_contact.can_edit
    except OrganisationContact.DoesNotExist:
        pass
    return False

def is_consultant(organisation,user):
    from commercialoperator.components.organisations.models import Organisation, OrganisationAccessGroup,UserDelegation,OrganisationContact
    from ledger.accounts.models import EmailUser
    try:
        org_contact=OrganisationContact.objects.get(organisation_id=organisation,email=user.email)
        # if org_contact.can_edit

        return org_contact.check_consultant
    except OrganisationContact.DoesNotExist:
        pass
    return False

def random_generator(size=12, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
