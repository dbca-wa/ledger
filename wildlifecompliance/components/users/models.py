from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.contrib.auth.models import Group
from ledger.accounts.models import EmailUser


class RegionDistrict(models.Model):

    DISTRICT_PERTH_HILLS = 'PHD'
    DISTRICT_SWAN_COASTAL = 'SCD'
    DISTRICT_SWAN_REGION = 'SWAN'
    DISTRICT_BLACKWOOD = 'BWD'
    DISTRICT_WELLINGTON = 'WTN'
    DISTRICT_SOUTH_WEST_REGION = 'SWR'
    DISTRICT_DONNELLY = 'DON'
    DISTRICT_FRANKLAND = 'FRK'
    DISTRICT_WARREN_REGION = 'WR'
    DISTRICT_ALBANY = 'ALB'
    DISTRICT_ESPERANCE = 'ESP'
    DISTRICT_SOUTH_COAST_REGION = 'SCR'
    DISTRICT_EAST_KIMBERLEY = 'EKD'
    DISTRICT_WEST_KIMBERLEY = 'WKD'
    DISTRICT_KIMBERLEY_REGION = 'KIMB'
    DISTRICT_PILBARA_REGION = 'PIL'
    DISTRICT_EXMOUTH = 'EXM'
    DISTRICT_GOLDFIELDS_REGION = 'GLD'
    DISTRICT_GERALDTON = 'GER'
    DISTRICT_KALBARRI = 'KLB'
    DISTRICT_MOORA = 'MOR'
    DISTRICT_SHARK_BAY = 'SHB'
    DISTRICT_MIDWEST_REGION = 'MWR'
    DISTRICT_CENTRAL_WHEATBELT = 'CWB'
    DISTRICT_SOUTHERN_WHEATBELT = 'SWB'
    DISTRICT_WHEATBELT_REGION = 'WBR'
    DISTRICT_AVIATION = 'AV'
    DISTRICT_OTHER = 'OTH'
    DISTRICT_KENSINGTON = 'KENSINGTON'
    
    DISTRICT_CHOICES = (
        (DISTRICT_SWAN_REGION, "Swan Region"),
        (DISTRICT_PERTH_HILLS, "Perth Hills"),
        (DISTRICT_SWAN_COASTAL, "Swan Coastal"),
        (DISTRICT_SOUTH_WEST_REGION, "South West Region"),
        (DISTRICT_BLACKWOOD, "Blackwood"),
        (DISTRICT_WELLINGTON, "Wellington"),
        (DISTRICT_WARREN_REGION, "Warren Region"),
        (DISTRICT_DONNELLY, "Donnelly"),
        (DISTRICT_FRANKLAND, "Frankland"),
        (DISTRICT_SOUTH_COAST_REGION, "South Coast Region"),
        (DISTRICT_ALBANY, "Albany"),
        (DISTRICT_ESPERANCE, "Esperance"),
        (DISTRICT_KIMBERLEY_REGION, "Kimberley Region"),
        (DISTRICT_EAST_KIMBERLEY, "East Kimberley"),
        (DISTRICT_WEST_KIMBERLEY, "West Kimberley"),
        (DISTRICT_PILBARA_REGION, "Pilbara Region"),
        (DISTRICT_EXMOUTH, "Exmouth"),
        (DISTRICT_GOLDFIELDS_REGION, "Goldfields Region"),
        (DISTRICT_MIDWEST_REGION, "Midwest Region"),
        (DISTRICT_GERALDTON, "Geraldton"),
        (DISTRICT_KALBARRI, "Kalbarri"),
        (DISTRICT_MOORA, "Moora"),
        (DISTRICT_SHARK_BAY, "Shark Bay"),
        (DISTRICT_WHEATBELT_REGION, "Wheatbelt Region"),
        (DISTRICT_CENTRAL_WHEATBELT, "Central Wheatbelt"),
        (DISTRICT_SOUTHERN_WHEATBELT, "Southern Wheatbelt"),
        (DISTRICT_AVIATION, "Aviation"),
        (DISTRICT_OTHER, "Other"),
        (DISTRICT_KENSINGTON, "Kensington"),
    )

    district = models.CharField(max_length=32, 
        choices=DISTRICT_CHOICES, 
        default=DISTRICT_OTHER)

    region = models.ForeignKey(
        'self',
        blank=True,
        null=True,
        related_name='districts')

    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Region District'
        verbose_name_plural = 'CM_Region Districts'

    def __str__(self):
        return self.get_district_display()

    @property
    def display_name(self):
        return self.__str__


class CompliancePermissionGroup(Group):

    region_district = models.ManyToManyField(
        'wildlifecompliance.RegionDistrict',
        blank=True)
    
    class Meta:
        app_label = 'wildlifecompliance'
        verbose_name = 'CM_Compliance Permission group'
        verbose_name_plural = 'CM_Compliance permission groups'
        # default_permissions = ()

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
