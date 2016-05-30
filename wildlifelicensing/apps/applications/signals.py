from datetime import date

from django.dispatch import receiver

from ledger.licence.models import Licence
from ledger.accounts.signals import name_changed

from wildlifelicensing.apps.main.signals import identification_uploaded
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.applications.views.process import determine_processing_status, determine_customer_status
from wildlifelicensing.apps.applications.emails import send_user_name_change_notification_email

from wildlifelicensing.apps.main.models import Licence


@receiver(name_changed)
def name_changed_callback(sender, **kwargs):
    if 'user' in kwargs:
        for licence in Licence.objects.filter(holder=kwargs.get('user'), end_date__gt=date.today()):
            send_user_name_change_notification_email(licence)


@receiver(identification_uploaded)
def identification_uploaded_callback(sender, **kwargs):
    if 'user' in kwargs:
        for application in Application.objects.filter(applicant_profile__user=kwargs.get('user')):
            if application.id_check_status == 'awaiting_update':
                application.id_check_status = 'updated'
                application.customer_status = determine_customer_status(application)
                application.processing_status = determine_processing_status(application)
                application.save()
