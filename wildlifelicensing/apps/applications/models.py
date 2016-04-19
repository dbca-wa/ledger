from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from ledger.accounts.models import EmailUser, Profile, Document, RevisionedMixin
from wildlifelicensing.apps.main.models import WildlifeLicenceType, Condition, AbstractLogEntry,\
    AssessorDepartment


class Application(RevisionedMixin):
    CUSTOMER_STATUS_CHOICES = (('draft', 'Draft'), ('pending', 'Pending'), ('under_review', 'Under Review'),
                               ('amendment_required', 'Amendment Required'), ('approved', 'Approved'),
                               ('rejected', 'Rejected'))

    PROCESSING_STATUS_CHOICES = (('draft', 'Draft'), ('new', 'New'), ('ready_for_action', 'Ready for Action'),
                                 ('awaiting_applicant_response', 'Awaiting Applicant Response'),
                                 ('awaiting_assessor_response', 'Awaiting Assessor Response'),
                                 ('awaiting_responses', 'Awaiting Responses'), ('ready_for_conditions', 'Ready for Conditions'),
                                 ('rejected', 'Rejected'))

    ID_CHECK_STATUS_CHOICES = (('not_checked', 'Not Checked'), ('awaiting_update', 'Awaiting Update'),
                               ('updated', 'Updated'), ('accepted', 'Accepted'))

    CHARACTER_CHECK_STATUS_CHOICES = (
        ('not_checked', 'Not Checked'), ('accepted', 'Accepted'), ('rejected', 'Rejected'))

    REVIEW_STATUS_CHOICES = (
        ('not_reviewed', 'Not Reviewed'), ('awaiting_amendments', 'Awaiting Amendments'), ('amended', 'Amended'),
        ('accepted', 'Accepted'), ('rejected', 'Rejected'))

    licence_type = models.ForeignKey(WildlifeLicenceType)
    customer_status = models.CharField('Customer Status', max_length=20, choices=CUSTOMER_STATUS_CHOICES,
                                       default=CUSTOMER_STATUS_CHOICES[0][0])
    data = JSONField()
    documents = models.ManyToManyField(Document)
    applicant_profile = models.ForeignKey(Profile)

    lodgement_number = models.CharField(max_length=9, blank=True, default='')
    lodgement_sequence = models.IntegerField(blank=True, default=0)
    lodgement_date = models.DateTimeField(blank=True, null=True)

    assigned_officer = models.ForeignKey(EmailUser, blank=True, null=True)
    processing_status = models.CharField('Processing Status', max_length=30, choices=PROCESSING_STATUS_CHOICES,
                                         default=PROCESSING_STATUS_CHOICES[0][0])
    id_check_status = models.CharField('Identification Check Status', max_length=20, choices=ID_CHECK_STATUS_CHOICES,
                                       default=ID_CHECK_STATUS_CHOICES[0][0])
    character_check_status = models.CharField('Character Check Status', max_length=20,
                                              choices=CHARACTER_CHECK_STATUS_CHOICES,
                                              default=CHARACTER_CHECK_STATUS_CHOICES[0][0])
    review_status = models.CharField('Review Status', max_length=20, choices=REVIEW_STATUS_CHOICES,
                                     default=REVIEW_STATUS_CHOICES[0][0])

    conditions = models.ManyToManyField(Condition, through='ApplicationCondition')

    @property
    def is_assigned(self):
        return self.assigned_officer is not None


class ApplicationLogEntry(AbstractLogEntry):
    application = models.ForeignKey(Application)


class AmendmentRequest(ApplicationLogEntry):
    STATUS_CHOICES = (('requested', 'Requested'), ('amended', 'Amended'))
    status = models.CharField('Status', max_length=30, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])


class AssessmentRequest(ApplicationLogEntry):
    STATUS_CHOICES = (('awaiting_assessment', 'Awaiting Assessment'), ('assessed', 'Assessed'))
    assessor_department = models.ForeignKey(AssessorDepartment)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])


class AssessorComment(ApplicationLogEntry):
    assessment_request = models.ForeignKey(AssessmentRequest)


class ApplicationCondition(models.Model):
    condition = models.ForeignKey(Condition)
    application = models.ForeignKey(Application)
    order = models.IntegerField()

    class Meta:
        unique_together = ('condition', 'application', 'order')


class EmailLogEntry(ApplicationLogEntry):
    pass


@receiver(pre_delete, sender=Application)
def delete_documents(sender, instance, *args, **kwargs):
    for document in instance.documents.all():
        document.delete()
