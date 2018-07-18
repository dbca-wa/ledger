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


def is_officer(user):
    return user.is_authenticated() and (belongs_to(user, 'Marinastay Officers') or user.is_superuser)


def is_customer(user):
    """
    Test if the user is a customer
    Rules:
        Not an officer
    :param user:
    :return:
    """
    return user.is_authenticated() and not is_officer(user)


def get_all_officers():
    return EmailUser.objects.filter(groups__name='Marinastay Officers')

def can_view_campground(user,campground):
    #print  campground
    for g in campground.mooringareagroup_set.all():
        if user in g.members.all():
            return True
    #return True
    return False
#def can_view_campground(user,campground):
#    print "JASON"
#    from pprint import pprint
#    #pprint(vars(campground))
 #   #pprint(vars(campground.campgroundgroup_set))
#    #print "JASON END"
#
#    #for g in campground.campgroundgroup_set.all():
#    #    if user in g.members.all():
#    #        return True
#    return False
