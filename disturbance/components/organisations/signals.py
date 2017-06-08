from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save, post_save
from django.conf import settings

from disturbance.components.organisations.models import Organisation

class OrganisationListener(object):
    """
    Event listener for Organisation 
    """

    @staticmethod
    @receiver(pre_save, sender=Organisation)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = Organisation.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)

            if not instance._is_same(original_instance):
                instance.updated_on = timezone.now()
        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            instance.pin_two = instance._generate_pin()
            instance.pin_two = instance._generate_pin() 

