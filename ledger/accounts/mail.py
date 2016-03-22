from django.conf import settings
from django.core.mail import send_mail
from django_hosts.resolvers import reverse


# Send mail validation to user, the email should include a link to continue the
# auth process. This is a simple example, it could easilly be extended to
# render a template and send a fancy HTML email instead.

def send_validation(strategy, backend, code):
    # TODO why the following url doesn't work for the token verification/login? (Exception 'missing parameter email')
    # TODO Only the wl works even if the views are identical.
    # url = reverse('accounts:token_login', args=(code.code,), host='ledger')
    url = reverse('dashboard:verification', args=(code.code,), host='wildlifelicensing')
    url = strategy.request.build_absolute_uri(url)
    send_mail('Passwordless Login', 'Use this URL to login {0}'.format(url),
              settings.EMAIL_FROM, [code.email], fail_silently=False)
