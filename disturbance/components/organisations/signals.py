from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save, post_save
from django.conf import settings

from disturbance.components.organisations.models import OrganisationRequest

class OrganisationRequestListener(object):
    """
    Event listener for CampgroundBookingRange
    """

    @staticmethod
    @receiver(pre_save, sender=CampgroundBookingRange)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = CampgroundBookingRange.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)

            if not instance._is_same(original_instance):
                instance.updated_on = timezone.now()
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
           pass 

