from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from preserialize.serialize import serialize

from ledger.accounts.models import Persona, Document
from ledger.accounts.forms import AddressForm, PersonaForm

from forms import IdentificationForm
from mixins import CustomerRequiredMixin


class ListPersonasView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/list_personas.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ListPersonasView, self).get_context_data(**kwargs)

        context['data'] = serialize(Persona.objects.filter(user=self.request.user))

        return context


class CreatePersonasView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/create_persona.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'persona_form': PersonaForm(),
                                                    'address_form': AddressForm()})

    def post(self, request, *args, **kwargs):
        persona_form = PersonaForm(request.POST)
        address_form = AddressForm(request.POST)

        if persona_form.is_valid() and address_form.is_valid():
            persona = persona_form.save(commit=False)
            persona.postal_address = address_form.save()
            persona.user = request.user
            persona.save()
        else:
            return render(request, self.template_name, {'persona_form': persona_form,
                                                        'address_form': address_form})

        messages.success(request, "The persona '%s' was created." % persona.name)

        return redirect('main:list_personas')


class EditPersonasView(CustomerRequiredMixin, TemplateView):
    template_name = 'wl/edit_persona.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        persona = get_object_or_404(Persona, pk=args[0])

        if persona.user != request.user:
            return HttpResponse('Unauthorized', status=401)

        return render(request, self.template_name, {'persona_form': PersonaForm(instance=persona),
                                                    'address_form': AddressForm(instance=persona.postal_address)})

    def post(self, request, *args, **kwargs):
        persona = get_object_or_404(Persona, pk=args[0])

        if persona.user != request.user:
            return HttpResponse('Unauthorized', status=401)

        persona_form = PersonaForm(request.POST, instance=persona)
        address_form = AddressForm(request.POST, instance=persona.postal_address)

        if persona_form.is_valid() and address_form.is_valid():
            persona.save()
            address_form.save()
        else:
            return render(request, self.template_name, {'persona_form': PersonaForm(instance=persona),
                                                        'address_form': AddressForm(instance=persona.postal_address)})

        messages.success(request, "The persona '%s' was updated." % persona.name)

        return redirect('main:list_personas')


class IdentificationView(LoginRequiredMixin, FormView):
    template_name = 'wl/manage_identification.html'
    login_url = '/'
    form_class = IdentificationForm
    success_url = '.'

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
