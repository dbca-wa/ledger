from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView

from preserialize.serialize import serialize

from ledger.accounts.models import Persona
from ledger.accounts.forms import AddressForm, PersonaForm


class ListPersonasView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/list_personas.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        context = super(ListPersonasView, self).get_context_data(**kwargs)

        context['data'] = serialize(Persona.objects.filter(user=self.request.user))

        return context


class CreatePersonasView(LoginRequiredMixin, TemplateView):
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
            return render(request, self.template_name, {'persona_form': PersonaForm(instance=persona),
                                                        'address_form': AddressForm(instance=persona.postal_address)})

        messages.success(request, "The persona '%s' was created." % persona.name)

        return redirect('main:list_personas')


class EditPersonasView(LoginRequiredMixin, TemplateView):
    template_name = 'wl/edit_persona.html'
    login_url = '/'

    def get(self, request, *args, **kwargs):
        persona = None

        try:
            persona = Persona.objects.get(pk=args[0])
        except Persona.DoesNotExist:
            return HttpResponse('Persona not found', status=404)

        if persona.user != request.user:
            return HttpResponse('Unauthorized', status=401)

        return render(request, self.template_name, {'persona_form': PersonaForm(instance=persona),
                                                    'address_form': AddressForm(instance=persona.postal_address)})

    def post(self, request, *args, **kwargs):
        persona = None

        try:
            persona = Persona.objects.get(pk=args[0])
        except Persona.DoesNotExist:
            return HttpResponse('Persona not found', status=404)

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
