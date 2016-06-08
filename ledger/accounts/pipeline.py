#from django.contrib.auth.models import User
from .models import EmailUser, EmailIdentity
from django.contrib.auth import logout

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
            user = EmailIdentity.objects.get(email=details['email']).user
        except EmailIdentity.DoesNotExist:
            user = None
        return {'user': user}
