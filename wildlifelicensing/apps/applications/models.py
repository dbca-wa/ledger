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

    PROCESSING_STATUS_CHOICES = (('draft', 'Draft'), ('new', 'New'), ('ready_for_action', 'Ready for Action'),
                                 ('awaiting_applicant_response', 'Awaiting Applicant Response'),
                                 ('awaiting_assessor_response', 'Awaiting Assessor Response'),
                                 ('awaiting_responses', 'Awaiting Responses'), ('approved', 'Approved'),
                                 ('rejected', 'Rejected'))

    ID_CHECK_STATUS_CHOICES = (('not_checked', 'Not Checked'), ('awaiting_update', 'Awaiting Update'),
                               ('updated', 'Updated'), ('accepted', 'Accepted'))

    CHARACTER_CHECK_STATUS_CHOICES = (('not_checked', 'Not Checked'), ('accepted', 'Accepted'), ('rejected', 'Rejected'))

    REVIEW_STATUS_CHOICES = (('not_reviewed', 'Not Reviewed'), ('awaiting_amendments', 'Awaiting Amendments'), ('amended', 'Amended'),
                             ('accepted', 'Accepted'), ('rejected', 'Rejected'))

    licence_type = models.ForeignKey(WildlifeLicenceType)
    customer_status = models.CharField('Customer Status', max_length=20, choices=CUSTOMER_STATUS_CHOICES, default=CUSTOMER_STATUS_CHOICES[0][0])
    data = JSONField()
    documents = models.ManyToManyField(Document)
    applicant_persona = models.ForeignKey(Persona)
    lodged_date = models.DateTimeField(blank=True, null=True)

    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True)
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[0][0])
    id_check_status = models.CharField('Identification Check Status', max_length=20, choices=ID_CHECK_STATUS_CHOICES,
                                       default=ID_CHECK_STATUS_CHOICES[0][0])
    character_check_status = models.CharField('Character Check Status', max_length=20, choices=CHARACTER_CHECK_STATUS_CHOICES,
                                              default=CHARACTER_CHECK_STATUS_CHOICES[0][0])
    review_status = models.CharField('Review Status', max_length=20, choices=REVIEW_STATUS_CHOICES,
                                     default=REVIEW_STATUS_CHOICES[0][0])

    assessments = models.ManyToManyField(EmailUser, through='Assessment', through_fields=('application', 'assessor'), related_name='Assessments')

    conditions = models.ManyToManyField(Condition)
    notes = models.TextField('Notes', blank=True)

    @property
    def is_assigned(self):
        return self.assigned_officer is not None


class AmendmentRequest(RevisionedMixin):
    STATUS_CHOICES = (('requested', 'Requested'), ('amended', 'Amended'))
    text = models.TextField(blank=True)
    status = models.CharField('Status', max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    application = models.ForeignKey(Application)


class Assessment(RevisionedMixin):
    STATUS_CHOICES = (('awaiting_assessment', 'Awaiting Assessment'), ('assessed', 'Assessed'))

    assessor = models.ForeignKey(EmailUser)
    application = models.ForeignKey(Application)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])


class AssessorComment(RevisionedMixin):
    text = models.TextField(blank=True)
    assessment = models.ForeignKey(Assessment)


@receiver(pre_delete, sender=Application)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()
