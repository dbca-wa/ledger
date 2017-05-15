
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from datetime import datetime, timedelta

from disturbance.helpers import is_officer
from disturbance.forms import LoginForm


class DashboardView(UserPassesTestMixin, TemplateView):
    template_name = 'disturbance/dash/index.html'

    def test_func(self):
        return is_officer(self.request.user)


class MyProposalsView(LoginRequiredMixin, TemplateView):
    template_name = 'disturbance/dash/index.html'


class DisturbanceRoutingView(TemplateView):
    template_name = 'disturbance/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_officer(self.request.user):
                return redirect('dash')
            return redirect('my-bookings')
        kwargs['form'] = LoginForm
        return super(DisturbanceRoutingView, self).get(*args, **kwargs)
