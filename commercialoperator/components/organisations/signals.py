from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_save, post_save
from django.conf import settings

from commercialoperator.components.organisations.models import Organisation,OrganisationContact
from ledger.accounts.models import EmailUser

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

        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        else:
            #instance.pin_one = instance._generate_pin()
            #instance.pin_two = instance._generate_pin()
            instance.admin_pin_one = instance._generate_pin()
            instance.admin_pin_two = instance._generate_pin() 
            instance.user_pin_one = instance._generate_pin()
            instance.user_pin_two = instance._generate_pin()  

class EmailUserUpdateContactListener(object):
    @staticmethod
    @receiver(post_save, sender=EmailUser)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if original_instance:
            try:
                OrganisationContact.objects.filter(email=original_instance.email).update(
                    first_name = instance.first_name,
                    last_name = instance.last_name,
                    mobile_number = instance.mobile_number,
                    phone_number = instance.phone_number,
                    fax_number = instance.fax_number,
                    email = instance.email
                )
            except EmailUser.DoesNotExist:
                pass
