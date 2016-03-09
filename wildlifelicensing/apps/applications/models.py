from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField

from licence.models import LicenceType
from rollcall.models import EmailUser


class Application(models.Model):
    models.ForeignKey(LicenceType)
    models.ForeignKey(EmailUser)
    JSONField('questions')