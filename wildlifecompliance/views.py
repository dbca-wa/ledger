from django.http import Http404, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from datetime import datetime, timedelta

from wildlifecompliance.helpers import is_officer, is_departmentUser
from wildlifecompliance.forms import *
from wildlifecompliance.components.applications.models import Referral,Application
from wildlifecompliance.components.applications.mixins import ReferralOwnerMixin

class ExternalApplicationView(DetailView):
    model = Application
    template_name = 'wildlifecompliance/dash/index.html'

class InternalView(UserPassesTestMixin, TemplateView):
    template_name = 'wildlifecompliance/dash/index.html'

    def test_func(self):
        return is_officer(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(InternalView, self).get_context_data(**kwargs)
        context['dev'] = settings.DEV_STATIC
        context['dev_url'] = settings.DEV_STATIC_URL
        return context

class ExternalView(LoginRequiredMixin, TemplateView):
    template_name = 'wildlifecompliance/dash/index.html'

    def get_context_data(self, **kwargs):
        context = super(ExternalView, self).get_context_data(**kwargs)
        context['dev'] = settings.DEV_STATIC
        context['dev_url'] = settings.DEV_STATIC_URL
        return context

class ReferralView(ReferralOwnerMixin, DetailView):
    model = Referral
    template_name = 'wildlifecompliance/dash/index.html'

class ApplicationView(ReferralOwnerMixin,DetailView):
    model=Application
    template_name='wildlifecompliance/dash/index.html'

class WildlifeComplianceRoutingView(TemplateView):
    template_name = 'wildlifecompliance/index.html'

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if is_officer(self.request.user) or is_departmentUser(self.request.user):
                return redirect('internal')
            return redirect('external')
        kwargs['form'] = LoginForm
        return super(WildlifeComplianceRoutingView, self).get(*args, **kwargs)

@login_required(login_url='wc_home')
def first_time(request):
    context = {}
    if request.method == 'POST':
        form = FirstTimeForm(request.POST)
        redirect_url = form.data['redirect_url']
        if not redirect_url:
            redirect_url = '/'
        if form.is_valid():
            # set user attributes
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.dob = form.cleaned_data['dob']
            request.user.save()
            return redirect(redirect_url)
        context['form'] = form
        context['redirect_url'] = redirect_url
        return render(request, 'wildlifecompliance/user_profile.html', context)
    # GET default
    if 'next' in request.GET:
        context['redirect_url'] = request.GET['next']
    else:
        context['redirect_url'] = '/'
    context['dev'] = settings.DEV_STATIC
    context['dev_url'] = settings.DEV_STATIC_URL
    return render(request, 'wildlifecompliance/dash/index.html', context)


class HealthCheckView(TemplateView):
    """A basic template view not requiring auth, used for service monitoring.
    """
    template_name = 'wildlifecompliance/healthcheck.html'

    def get_context_data(self, **kwargs):
        context = super(HealthCheckView, self).get_context_data(**kwargs)
        context['page_title'] = 'Wildlife Compliance application status'
        context['status'] = 'HEALTHY'
        return context
