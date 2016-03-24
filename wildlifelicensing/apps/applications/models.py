from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from ledger.accounts.models import Persona, Document
from ledger.licence.models import LicenceType


class Application(models.Model):
    STATUS_CHOICES = (('draft', 'Draft'), ('lodged', 'Lodged'))

    licence_type = models.ForeignKey(LicenceType)
    applicant_persona = models.ForeignKey(Persona)
    status = models.CharField('Application State', max_length=20, choices=STATUS_CHOICES)
    data = JSONField()
    documents = models.ManyToManyField(Document)


@receiver(pre_delete, sender=Application)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()
