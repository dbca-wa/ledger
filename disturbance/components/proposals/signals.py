from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from disturbance.components.proposals.models import (
    ProposalAssessorGroup,
    Referral
)

class ProposalAssessorGroupListener(object):
    """
    Event listener for ProposalAssessorGroup 
    """

    @staticmethod
    @receiver(pre_save, sender=ProposalAssessorGroup)
    def _pre_save(sender, instance, **kwargs):
        if instance.pk:
            original_instance = ProposalAssessorGroup.objects.get(pk=instance.pk)
            setattr(instance, "_original_instance", original_instance)

        elif hasattr(instance, "_original_instance"):
            delattr(instance, "_original_instance")
        instance.full_clean()

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
            # Check if the proposal attached to the referral outstanding referrals
            outstanding  = instance.proposal.referrals.filter(processing_status='with_referral') 
            if len(outstanding) == 0:
                instance.proposal.processing_status = 'with_assessor'
                instance.proposal.save()
                
