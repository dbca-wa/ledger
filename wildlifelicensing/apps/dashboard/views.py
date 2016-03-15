from __future__ import unicode_literals

import logging
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import View, RedirectView, TemplateView, FormView
from django.contrib.auth.models import Group

from braces.views import LoginRequiredMixin

from customers.models import Address, Customer
from .forms import CustomerCreateForm


logger = logging.getLogger(__name__)


class DashBoardView(TemplateView):
    template_name = 'wl/index.html'

    def get(self, *args, **kwargs):
        redirect_url = None
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name='Customers').exists():
                redirect_url = None
            elif self.request.user.groups.filter(name='Officers').exists():
                redirect_url = None
        if redirect_url:
            return redirect(redirect_url)
        else:
            return super(DashBoardView, self).get(*args, **kwargs)


class VerificationView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        redirect_url = '{}?verification_code={}'.format(
            reverse('social:complete', args=('email',)),
            kwargs['token']
        )
        if self.request.user and hasattr(self.request.user, 'email'):
            redirect_url += '&email={}'.format(self.request.user.email)
        return redirect_url


class ValidationSentView(View):
    def get(self, *args, **kwargs):
        messages.success(self.request,
                         "An email has been sent to you. "
                         "Check your mailbox and click on the link to complete the login process.")
        return redirect('home')



