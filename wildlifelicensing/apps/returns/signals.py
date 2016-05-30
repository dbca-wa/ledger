from django.dispatch import receiver

from wildlifelicensing.apps.main.signals import licence_issued
from wildlifelicensing.apps.main.models import WildlifeLicence
from wildlifelicensing.apps.returns.utils import create_returns_due_dates
from wildlifelicensing.apps.returns.models import ReturnType, Return
from django.shortcuts import get_object_or_404


@receiver(licence_issued)
def licence_issued_callback(sender, **kwargs):
    if 'wildlife_licence' in kwargs:
        licence = WildlifeLicence.objects.get(pk=kwargs.get('wildlife_licence'))

        due_dates = create_returns_due_dates(licence.start_date, licence.end_date, licence.return_frequency)

        Return.objects.filter(licence=licence).delete()

        return_type = get_object_or_404(ReturnType, licence_type=licence.licence_type)

        returns = []
        for due_date in due_dates:
            returns.append(Return(licence=licence, return_type=return_type, due_date=due_date))

        Return.objects.bulk_create(returns)
