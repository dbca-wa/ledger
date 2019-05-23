from django.contrib.auth.models import Group
from ledger.accounts.models import EmailUser


class CompliancePermissionGroup(Group):
    # licence_activities = models.ManyToManyField(
    #     'wildlifecompliance.LicenceActivity',
    #     blank=True)

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'Activity permission group'
        verbose_name_plural = 'Activity permission groups'

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

    # @staticmethod
    # def get_groups_for_activities(activities, codename):
    #     """
    #     Find matching ActivityPermissionGroups for a list of activities, activity ID or a LicenceActivity instance.
    #     :return: ActivityPermissionGroup QuerySet
    #     """
    #     from wildlifecompliance.components.licences.models import LicenceActivity

    #     if isinstance(activities, LicenceActivity):
    #         activities = [activities.id]

    #     groups = ActivityPermissionGroup.objects.filter(
    #         licence_activities__id__in=activities if isinstance(
    #             activities, (list, QuerySet)) else [activities]
    #     )
    #     if isinstance(codename, list):
    #         groups = groups.filter(permissions__codename__in=codename)
    #     else:
    #         groups = groups.filter(permissions__codename=codename)
    #     return groups.distinct()