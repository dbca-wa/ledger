from django.dispatch import receiver

from wildlifelicensing.apps.main.signals import identification_uploaded

from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.applications.views.process import determine_processing_status, determine_customer_status


@receiver(identification_uploaded)
def identification_uploaded_callback(sender, **kwargs):
    if 'user' in kwargs:
        for application in Application.objects.filter(applicant_profile__user=kwargs.get('user')):
            if application.id_check_status == 'awaiting_update':
                application.id_check_status = 'updated'
                application.customer_status = determine_customer_status(application)
                application.processing_status = determine_processing_status(application)
                application.save()
