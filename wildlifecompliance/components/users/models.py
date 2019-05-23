from django.contrib.auth.models import Group
from ledger.accounts.models import EmailUser


class CompliancePermissionGroup(Group):

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'Compliance permission group'
        verbose_name_plural = 'Compliance permission groups'

    def __str__(self):
        return '{} ({} members)'.format(
            self.name,
            EmailUser.objects.filter(groups__name=self.name).count()
        )

    @property
    def display_name(self):
        return self.__str__

    @property
    def members(self):
        return EmailUser.objects.filter(
            groups__id=self.id
        ).distinct()
