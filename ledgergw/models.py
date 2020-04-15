from __future__ import unicode_literals

import os
import zlib

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.contrib.postgres.fields import JSONField
from django.db import models, IntegrityError, transaction
from django.utils import timezone
from django.dispatch import receiver
from django.db.models import Q
from django.db.models.signals import post_delete, pre_save, post_save
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from django_countries.fields import CountryField
from django.utils.crypto import get_random_string

from datetime import datetime, date



class API(models.Model):
    STATUS = (
       (0, 'Inactive'),
       (1, 'Active'),
    )


    system_name = models.CharField(max_length=512)
    system_id = models.CharField(max_length=4, null=True, blank=True)
    api_key = models.CharField(max_length=512,null=True, blank=True, default='')
    allowed_ips = models.TextField(null=True, blank=True, default='')
    active = models.SmallIntegerField(choices=STATUS, default=0) 

    def save(self, *args, **kwargs):
        if self.api_key is not None:

             if len(self.api_key) > 1:
                  pass
             else:
                  self.api_key = self.get_random_key(100)
        else:
            self.api_key = self.get_random_key(100)
        super(API,self).save(*args,**kwargs)


    def get_random_key(self,key_length=100):
        return get_random_string(length=key_length, allowed_chars=u'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

