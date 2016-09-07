from datetime import date

from django.dispatch import receiver
from django.contrib import messages

from ledger.accounts.signals import name_changed

from wildlifelicensing.apps.main.signals import identification_uploaded
from wildlifelicensing.apps.main.models import Licence
from wildlifelicensing.apps.applications.models import Application
from wildlifelicensing.apps.applications.views.process import determine_processing_status, determine_customer_status
from wildlifelicensing.apps.applications.emails import send_user_name_change_notification_email
from wildlifelicensing.apps.returns.signals import return_submitted
from wildlifelicensing.apps.returns.models import Return


@receiver(name_changed)
def name_changed_callback(sender, **kwargs):
    if 'user' in kwargs:
        for licence in Licence.objects.filter(holder=kwargs.get('user'), end_date__gt=date.today()):
            send_user_name_change_notification_email(licence)


@receiver(identification_uploaded)
def identification_uploaded_callback(sender, **kwargs):
    if 'request' in kwargs:
        request = kwargs.get('request')
        is_app_awaiting_id_check = False
        for application in Application.objects.filter(applicant_profile__user=request.user):
            if application.id_check_status == 'awaiting_update':
                application.id_check_status = 'updated'
                application.customer_status = determine_customer_status(application)
                application.processing_status = determine_processing_status(application)
                application.save()

                is_app_awaiting_id_check = True

        if is_app_awaiting_id_check:
            messages.success(request, 'Thank you for providing your photographic identification. Any application(s) '
                             'currently awaiting this identification will now proceed with processing.')


@receiver(return_submitted)
def return_submitted_callback(sender, **kwargs):
    if 'ret' in kwargs:
        ret = kwargs.get('ret')
        try:
            previous_application = Application.objects.get(licence=ret.licence)
            application = Application.objects.get(previous_application=previous_application)
            if application.returns_check_status == 'awaiting_returns':
                if not Return.objects.filter(licence=ret.licence).exclude(status='submitted').\
                        exclude(status='approved').exists():
                    application.returns_check_status = 'completed'
                    application.customer_status = determine_customer_status(application)
                    application.processing_status = determine_processing_status(application)
                    application.save()
        except Application.DoesNotExist:
            pass
