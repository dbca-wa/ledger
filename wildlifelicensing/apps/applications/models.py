from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from ledger.accounts.models import EmailUser, Document
from ledger.licence.models import LicenceType


class Application(models.Model):
    STATES = (('draft', 'Draft'), ('lodged', 'Lodged'))
    licence_type = models.ForeignKey(LicenceType, null=True)
    applicant = models.ForeignKey(EmailUser)
    state = models.CharField('Application State', max_length=20, choices=STATES)
    data = JSONField()
    documents = models.ManyToManyField(Document)


@receiver(pre_delete, sender=Application)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()
