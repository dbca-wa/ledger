from __future__ import unicode_literals
from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.postgres.fields import ArrayField

from dbca_utils.models import ActiveMixin

from ledger.accounts.models import RevisionedMixin


@python_2_unicode_compatible
class LicenceType(RevisionedMixin, ActiveMixin):
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=30, blank=True, null=True,
                                  help_text="The display name that will show in the dashboard")
    version = models.SmallIntegerField(default=1, blank=False, null=False)
    code = models.CharField(max_length=64)
    act = models.CharField(max_length=256, blank=True)
    statement = models.TextField(blank=True)
    authority = models.CharField(max_length=64, blank=True)
    replaced_by = models.ForeignKey(
        'self', on_delete=models.PROTECT, blank=True, null=True)
    is_renewable = models.BooleanField(default=True)
    keywords = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        result = self.short_name or self.name
        if self.replaced_by is None:
            return result
        else:
            return '{} (V{})'.format(result, self.version)

    @property
    def is_obsolete(self):
        return self.replaced_by is not None

    class Meta:
        unique_together = ('short_name', 'version')


@python_2_unicode_compatible
class Licence(RevisionedMixin, ActiveMixin):
    holder = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='holder')
    issuer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='issuer',
                               blank=True, null=True)
    licence_type = models.ForeignKey(LicenceType, on_delete=models.PROTECT)
    licence_number = models.CharField(max_length=64, blank=True, null=True)
    licence_sequence = models.IntegerField(blank=True, default=0)
    issue_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_renewable = models.NullBooleanField(blank=True)

    class Meta:
        unique_together = ('licence_number', 'licence_sequence')

    def __str__(self):
        return '{} {}-{}'.format(self.licence_type, self.licence_number, self.licence_sequence)
