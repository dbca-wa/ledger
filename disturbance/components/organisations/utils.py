import string
import random


def can_manage_org(organisation,user):
    from disturbance.components.organisations.models import Organisation, OrganisationAccessGroup,UserDelegation
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


def is_last_admin(organisation, user):
    from disturbance.components.organisations.models import OrganisationContact
    ''' A check for whether the user contact is the only administrator for the Organisation. '''
    _last_admin = False
    try:
        _admin_contacts = OrganisationContact.objects.filter(organisation_id=organisation,
                                                             user_status='active',
                                                             user_role='organisation_admin')
        _is_admin = _admin_contacts.filter(email=user.email).exists()
        if _is_admin and _admin_contacts.count() < 2:
            _last_admin = True
    except OrganisationContact.DoesNotExist:
        _last_admin = False
    return _last_admin


def can_admin_org(organisation,user):
    from disturbance.components.organisations.models import Organisation, OrganisationAccessGroup,UserDelegation,OrganisationContact
    from ledger.accounts.models import EmailUser
    try:
        org_contact=OrganisationContact.objects.get(organisation_id=organisation,email=user.email)
        # if org_contact.can_edit

        return org_contact.can_edit
    except OrganisationContact.DoesNotExist:
        pass
    return False


def can_relink(organisation, user):
    from disturbance.components.organisations.models import OrganisationContact
    ''' Check user contact can be relinked to the Organisation. '''
    _can_relink = False
    try:
        _can_relink = OrganisationContact.objects.filter(organisation_id=organisation.id,
                                                         email=user.email,
                                                         user_status='unlinked').exists()
    except OrganisationContact.DoesNotExist:
        _can_relink = False
    return _can_relink


def can_approve(organisation, user):
    from disturbance.components.organisations.models import OrganisationContact
    ''' Check user contact linkage to the Organisation can be approved. '''
    _can_approve = False
    try:
        _can_approve = OrganisationContact.objects.filter(organisation_id=organisation.id,
                                                          email=user.email,
                                                          user_status__in=('declined', 'pending')).exists()
    except OrganisationContact.DoesNotExist:
        _can_approve = False
    return _can_approve


def is_consultant(organisation,user):
    from disturbance.components.organisations.models import Organisation, OrganisationAccessGroup,UserDelegation,OrganisationContact
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


def generate_new_pins():
    from disturbance.components.organisations.models import Organisation
    all_orgs=Organisation.objects.all()
    for org in all_orgs:
        org.generate_pins()

def activate_org_contacts():
    from disturbance.components.organisations.models import OrganisationContact
    try:
        all_contacts=OrganisationContact.objects.all()
        for contact in all_contacts:
            if contact.user_status=='draft':
                contact.user_status='active'
                contact.save()
                print contact
    except:
        pass

def add_admin_user():
    from disturbance.components.organisations.models import Organisation
    from disturbance.components.organisations.models import OrganisationContact
    all_orgs=Organisation.objects.all()
    for org in all_orgs:
        all_delegates=[]
        all_delegates=org.delegates.all()
        if all_delegates:
            first_delegate=org.delegates.first()
            try:
                all_admin_user= OrganisationContact.objects.filter(organisation = org,user_role='organisation_admin', is_admin=True, user_status='active')
                print all_admin_user.count()
                if all_admin_user.count<1:
                    org_contact = OrganisationContact.objects.get(organisation = org,email = first_delegate.email)
                    if org_contact.user_status=='draft':
                        org_contact.user_status='active'
                    org_contact.user_role ='organisation_admin'
                    org_contact.is_admin = True
                    org_contact.save()
                    print org_contact
            except OrganisationContact.DoesNotExist:
                pass    
