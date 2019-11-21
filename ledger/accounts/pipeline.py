#from django.contrib.auth.models import User
from social_core.exceptions import InvalidEmail
from django.core.exceptions import ValidationError
from .models import EmailUser, EmailIdentity
from django.contrib import messages
from django.contrib.auth import logout
from django.core.validators import validate_email
from django.urls import reverse

def mail_validation(backend, details, is_new=False, *args, **kwargs):
    requires_validation = backend.REQUIRES_EMAIL_VALIDATION or \
                          backend.setting('FORCE_EMAIL_VALIDATION', False)
    send_validation = details.get('email') and \
                      (is_new or backend.setting('PASSWORDLESS', False))
    if requires_validation and send_validation:
        data = backend.strategy.request_data()
        if 'verification_code' in data:     # sign-in URL request to authenticate a session
            backend.strategy.session_pop('email_validation_address')
            if not backend.strategy.validate_email(details['email'],
                                           data['verification_code']):
                return backend.strategy.redirect(
                    reverse('accounts:login_expired')
                )
            # validation successful, continue on
        else:       # need to generate a validation email then kick back to the login page
            try:
                validate_email(details['email'])
                backend.strategy.send_email_validation(backend,
                                                       details['email'])
                backend.strategy.session_set('email_validation_address',
                                             details['email'])
            except Exception as e:
                return backend.strategy.redirect(
                    reverse('accounts:login_retry')
                )
            return backend.strategy.redirect(
                backend.strategy.setting('EMAIL_VALIDATION_URL')
            )

#logout previous session if exists and does not match
def logout_previous_session(backend,details,user=None, *args, **kwargs):
    strategy = backend.strategy
    request_data = strategy.request_data()
    if request_data.get('verification_code') and details.get('email') and user and user.is_authenticated():
        if user.email != details["email"]:
            #already authenticated with another user, logout before.
            logout(strategy.request)
            return strategy.redirect("{}?verification_code={}&email={}".format(strategy.request_path(),request_data['verification_code'],request_data['email']))



#convert email address to lower case.
def lower_email_address(backend, details, *args, **kwargs):
    if "email" in details:
        details["email"] = details["email"].lower()

# Custom pipeline to retrieve the user by the email in the details and log it
# in. The code checks for a verification_code parameter in order to validate
# that this is a password-less auth attempt, that way other social
# authentication will keep working.

def user_by_email(backend, details, *args, **kwargs):
    request_data = backend.strategy.request_data()
    if request_data.get('verification_code') and details.get('email'):
        try:
            user = EmailIdentity.objects.filter(email__iexact=details['email'])[0].user
        except IndexError:
            user = None
        return {'user': user}


def user_is_new_session(backend, details, strategy, is_new=False, *args, **kwargs):
    backend.strategy.session_set('is_new',is_new)
