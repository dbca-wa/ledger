from __future__ import unicode_literals

from django.views.generic.edit import CreateView, FormView
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect

from rollcall.models import EmailUser


class LoginView(FormView):
    template_name = 'index.html'
    form_class = AuthenticationForm

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)

        if user.groups.filter(name='Applicants').exists():
            return redirect('applicants:dashboard')
        elif user.groups.filter(name='Officers').exists():
            return redirect('officers:dashboard')


class UserCreateView(CreateView):
    template_name = 'user_create.html'
    model = EmailUser
    success_url = reverse_lazy('home')
    fields = ['email']
