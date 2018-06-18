from django.db.models.signals import post_delete, pre_save, post_save, m2m_changed
from django.core.exceptions import ValidationError
from django.dispatch import receiver
from ledger.accounts.models import EmailUser
from wildlifecompliance.components.applications.models import (
    ApplicationAssessorGroup,
    Referral
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

class ReferralListener(object):
    """
    Event listener for Referral 
    """

    @staticmethod
    @receiver(pre_save, sender=Referral)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = Referral.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)

        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")

    @staticmethod
    @receiver(post_save, sender=Referral)
    def _post_save(sender, instance, **kwargs):
        original_instance = getattr(instance, "_original_instance") if hasattr(instance, "_original_instance") else None
        if original_instance:
            # Check if the application attached to the referral outstanding referrals
            outstanding  = instance.application.referrals.filter(processing_status='with_referral') 
            if len(outstanding) == 0:
                instance.application.processing_status = 'with_assessor'
                instance.application.save()
                
