from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import View, RedirectView, TemplateView
from django.views.generic.edit import CreateView

from rollcall.models import EmailUser


class DashBoardView(TemplateView):
    template_name = 'index.html'

    def get(self, *args, **kwargs):
        redirect_url = None
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name='Applicants').exists():
                redirect_url = 'applicants:dashboard'
            elif self.request.user.groups.filter(name='Officers').exists():
                redirect_url = 'officers:dashboard'
        if redirect_url:
            return redirect(redirect_url)
        else:
            return super(DashBoardView, self).get(*args, **kwargs)


class VerificationView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('social:complete', args=('email',)) + '?verification_code={}'.format(kwargs['token'])


class ValidationSentView(View):
    def get(self, *args, **kwargs):
        messages.success(self.request,
                         "An email has been sent to you. "
                         "Check your mailbox and click on the link to complete the login process.")
        return redirect('home')


class UserCreateView(CreateView):
    template_name = 'user_create.html'
    model = EmailUser
    success_url = reverse_lazy('home')
    fields = ['email']
