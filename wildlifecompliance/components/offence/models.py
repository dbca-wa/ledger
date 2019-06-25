from django.db import models
from ledger.accounts.models import RevisionedMixin, EmailUser
from wildlifecompliance.components.call_email.models import Location, CallEmail


class SectionRegulation(RevisionedMixin):
    act = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=50, blank=True)
    offence_text = models.CharField(max_length=200, blank=True)
    amount =  models.DecimalField(max_digits=8, decimal_places=2, default='0.00')


    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Section/Regulation'
        verbose_name_plural = 'CM_Sections/Regulations'
        ordering = ('act', 'name')

    def __str__(self):
        return '{}:{}:{}'.format(self.act, self.name, self.offence_text)


class Offence(RevisionedMixin):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('closing', 'Closing'),
        ('closed', 'Closed'),
    )

    identifier = models.CharField(
        max_length=50,
        blank=True,
    )
    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        default='draft',
    )
    location = models.ForeignKey(
        Location,
        null=True,
        blank=True,
        related_name="offence_location",
    )
    call_email = models.ForeignKey(
        CallEmail,
        null=True,
        blank=True,
        related_name='offence_call_eamil',
    )
    occurrence_from_to = models.BooleanField(default=False)
    occurrence_date_from = models.DateField(null=True, blank=True)
    occurrence_time_from = models.TimeField(null=True, blank=True)
    occurrence_date_to = models.DateField(null=True, blank=True)
    occurrence_time_to = models.TimeField(null=True, blank=True)
    alleged_offences = models.ManyToManyField(
        SectionRegulation,
        blank=True,
    )
    details = models.TextField(blank=True)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Offence'
        verbose_name_plural = 'CM_Offences'

    def __str__(self):
        return 'ID: {}, Status: {}, Identifier: {}'.format(self.id, self.status, self.identifier)
    
    @property
    def get_related_items_identifier(self):
        return '{}'.format(self.identifier)
    
    @property
    def get_related_items_descriptor(self):
        return '{}'.format(self.details)


class Offender(models.Model):
    reason_for_removal = models.TextField(blank=True)
    removed = models.BooleanField(default=False)
    removed_by = models.ForeignKey(
        EmailUser,
        null=True,
        related_name='offender_removed_by'
    )
    person = models.ForeignKey(
        EmailUser,
        null=True,
        related_name='offender_person',
    )
    offence = models.ForeignKey(
        Offence,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Offender'
        verbose_name_plural = 'CM_Offenders'

    def __str__(self):
        return 'First name: {}, Last name: {}'.format(self.person.first_name, self.person.last_name)
