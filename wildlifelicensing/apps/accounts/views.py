from __future__ import unicode_literals

from django.views.generic.edit import CreateView
from django.core.urlresolvers import reverse_lazy
from rollcall.models import EmailUser


class UserCreateView(CreateView):
    template_name = 'user_create.html'
    model = EmailUser
    success_url = reverse_lazy('home')
    fields = ['email']
