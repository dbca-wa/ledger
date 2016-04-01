from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from ledger.accounts.models import EmailUser, Persona, Document, RevisionedMixin
from wildlifelicensing.apps.main.models import WildlifeLicenceType, Condition


class Application(RevisionedMixin):
    CUSTOMER_STATUS_CHOICES = (('draft', 'Draft'), ('pending', 'Pending'), ('under_review', 'Under Review'),
                               ('amendment_required', 'Amendment Required'), ('approved', 'Approved'),
                               ('rejected', 'Rejected'))

    PROCESSING_STATUS_CHOICES = (('draft', 'Draft'), ('new', 'New'), ('incomplete', 'Incomplete'),
                                 ('amended', 'Amended'), ('ready_for_assessment', 'Ready for Assessment'),
                                 ('awaiting_assessment', 'Awaiting Assessment'), ('approved', 'Approved'),
                                 ('rejected', 'Rejected'))

    licence_type = models.ForeignKey(WildlifeLicenceType)
    customer_status = models.CharField('Customer Status', max_length=20, choices=CUSTOMER_STATUS_CHOICES)
    data = JSONField()
    documents = models.ManyToManyField(Document)
    applicant_persona = models.ForeignKey(Persona)
    lodged_date = models.DateTimeField(blank=True, null=True)

    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True)
    processing_status = models.CharField('Processing Status', max_length=20, choices=PROCESSING_STATUS_CHOICES)
    conditions = models.ManyToManyField(Condition)
    notes = models.TextField('Notes', blank=True)

    @property
    def is_assigned(self):
        return self.assigned_officer is not None


class AmendmentRequest(RevisionedMixin):
    text = models.TextField(blank=True)
    application = models.ForeignKey(Application)


class AssessorComment(RevisionedMixin):
    text = models.TextField(blank=True)
    application = models.ForeignKey(Application)


@receiver(pre_delete, sender=Application)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()
