from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from disturbance.components.proposals.models import (
    ProposalAssessorGroup
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
