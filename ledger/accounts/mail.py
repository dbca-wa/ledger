from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import loader


# Send mail validation to user, the email should include a link to continue the
# auth process. This is a simple example, it could easily be extended to
# render a template and send a fancy HTML email instead.

def send_validation(strategy, backend, code, partial_token=None):
    url = reverse('accounts:token_login', args=(code.code, code.email))
    url = strategy.request.build_absolute_uri(url)
    template = loader.render_to_string('email/login.txt', context={'login_url': url, 'system_name': settings.SYSTEM_NAME})

    send_mail('Your login URL for the customer portal', template,
              settings.DEFAULT_FROM_EMAIL, [code.email], fail_silently=False)
