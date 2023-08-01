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
from django.conf import settings

from datetime import datetime, date



class API(models.Model):
    STATUS = (
       (0, 'Inactive'),
       (1, 'Active'),
    )


    system_name = models.CharField(max_length=512)
    system_id = models.CharField(max_length=4, null=True, blank=True)
    api_key = models.CharField(max_length=512,null=True, blank=True, default='', help_text="Key is auto generated,  Leave blank or blank out to create a new key")
    allowed_ips = models.TextField(null=True, blank=True, default='', help_text="Use network ranges format: eg 1 ip = 10.1.1.1/32 or for a c class block of ips use 192.168.1.0/24 etc")
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




class JobQueue(models.Model):
    STATUS = (
       (0, 'Pending'),
       (1, 'Running'),
       (2, 'Completed'),
       (3, 'Failed'),
    )

    job_cmd = models.CharField(max_length=1000, null=True, blank=True)
    system_id = models.CharField(max_length=4, null=True, blank=True)
    status = models.SmallIntegerField(choices=STATUS, default=0) 
    parameters_json = models.TextField(null=True, blank=True)
    processed_dt = models.DateTimeField(default=None,null=True, blank=True )
    user = models.ForeignKey(settings.AUTH_USER_MODEL,default=None,null=True, blank=True )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.job_cmd   