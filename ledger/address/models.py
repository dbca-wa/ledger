from django.db import models
from oscar.apps.address.abstract_models import AbstractUserAddress

class UserAddress(AbstractUserAddress):
    profile_address = models.ForeignKey('accounts.Address', related_name='oscar_address',null=True,blank=True)


from oscar.apps.address.models import *  # noqa
