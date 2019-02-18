from django.db.models.signals import post_delete, pre_save, post_save, m2m_changed
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.applications.models import (
    ApplicationAssessorGroup
)

class ApplicationAssessorGroupListener(object):
    """
    Event listener for ApplicationAssessorGroup 
    """

    @staticmethod
    @receiver(pre_save, sender=ApplicationAssessorGroup)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = ApplicationAssessorGroup.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)

        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        instance.full_clean()
    
    @staticmethod
    @receiver(m2m_changed, sender=ApplicationAssessorGroup.members.through)
    def members_changed(sender,instance, action,**kwargs):
        if action == 'pre_remove':
            for o in EmailUser.objects.filter(id__in=kwargs.get('pk_set')):
                if instance.member_is_assigned(o):
                    raise ValidationError('{} is currently assigned to a application(s)'.format(o.email)) 

                
