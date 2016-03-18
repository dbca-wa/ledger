from __future__ import unicode_literals

import logging

from django.core.urlresolvers import reverse
from django.views.generic import RedirectView, TemplateView

logger = logging.getLogger(__name__)


class DashBoardView(TemplateView):
    template_name = 'wl/index.html'


# TODO This should be handle by the ledger view (see ledger/accounts/mail.py)
class VerificationView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        redirect_url = '{}?verification_code={}'.format(
            reverse('social:complete', args=('email',)),
            kwargs['token']
        )
        if self.request.user and hasattr(self.request.user, 'email'):
            redirect_url += '&email={}'.format(self.request.user.email)
        return redirect_url
