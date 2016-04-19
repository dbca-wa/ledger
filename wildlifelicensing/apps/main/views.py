from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from preserialize.serialize import serialize

from ledger.accounts.models import Profile, Document
from ledger.accounts.forms import AddressForm, ProfileForm

from forms import IdentificationForm
from mixins import CustomerRequiredMixin


class ListProfilesView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/list_profiles.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ListProfilesView, self).get_context_data(**kwargs)

        context['data'] = serialize(Profile.objects.filter(user=self.request.user))

        return context


class CreateProfilesView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/create_profile.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'profile_form': ProfileForm(),
                                                    'address_form': AddressForm()})

    def post(self, request, *args, **kwargs):
        profile_form = ProfileForm(request.POST)
        address_form = AddressForm(request.POST)

        if profile_form.is_valid() and address_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.postal_address = address_form.save()
            profile.user = request.user
            profile.save()
        else:
            return render(request, self.template_name, {'profile_form': profile_form,
                                                        'address_form': address_form})

        messages.success(request, "The profile '%s' was created." % profile.name)

        return redirect('main:list_profiles')


class EditProfilesView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/edit_profile.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=args[0])

        if profile.user != request.user:
            return HttpResponse('Unauthorized', status=401)

        return render(request, self.template_name, {'profile_form': ProfileForm(instance=profile),
                                                    'address_form': AddressForm(instance=profile.postal_address)})

    def post(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=args[0])

        if profile.user != request.user:
            return HttpResponse('Unauthorized', status=401)

        profile_form = ProfileForm(request.POST, instance=profile)
        address_form = AddressForm(request.POST, instance=profile.postal_address)

        if profile_form.is_valid() and address_form.is_valid():
            profile.save()
            address_form.save()
        else:
            return render(request, self.template_name, {'profile_form': ProfileForm(instance=profile),
                                                        'address_form': AddressForm(instance=profile.postal_address)})

        messages.success(request, "The profile '%s' was updated." % profile.name)

        return redirect('main:list_profiles')


class IdentificationView(LoginRequiredMixin, FormView):
    template_name = 'wl/manage_identification.html'
    login_url = '/'
    form_class = IdentificationForm
    success_url = reverse_lazy('main:identification')

    def form_valid(self, form):
        if self.request.user.identification is not None:
            self.request.user.identification.delete()

        self.request.user.identification = Document.objects.create(file=self.request.FILES['identification_file'])
        self.request.user.save()

        return super(IdentificationView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(IdentificationView, self).get_context_data(**kwargs)

        if self.request.user.identification is not None:
            context['existing_id_image_url'] = self.request.user.identification.file.url

        return context
