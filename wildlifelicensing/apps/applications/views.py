import json
import os

from django.views.generic.base import TemplateView
from django.shortcuts import render_to_response, redirect
from django.core.context_processors import csrf
from django.contrib import messages

from models import Application
from utils import create_data_from_form


class ApplicationsView(TemplateView):
    template_name = 'applications.html'

    def get_context_data(self, **kwargs):
        context = super(ApplicationsView, self).get_context_data(**kwargs)
        context['applications'] = {'regulation17': 'Application for a licence to take fauna for scientific purposes'}

        return context


class ApplicationView(TemplateView):
    template_name = 'application.html'

    def get(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_stucture = json.load(data_file)

        context = {'structure': form_stucture, 'application_type': args[0]}
        context.update(csrf(request))

        return render_to_response(self.template_name, context)

    def post(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_stucture = json.load(data_file)

        request.session['application_data'] = create_data_from_form(form_stucture, request.POST)  
        
        print request.POST.get('submit')
        
        if 'draft' in request.POST:
            Application.objects.create(data=request.session.get('application_data'), state='draft')

            messages.warning(request, 'The application was saved to draft.')

            return redirect('applications:applications')
        else:
            return redirect('applications:application_preview', args[0])


class ApplicationPreviewView(TemplateView):
    template_name = 'application_preview.html'

    def get(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_stucture = json.load(data_file)

        context = {'structure': form_stucture, 'application_type': args[0]}
        context.update(csrf(request))

        context['data'] = request.session.get('application_data')

        return render_to_response(self.template_name, context)

    def post(self, request, *args, **kwargs):
        Application.objects.create(data=request.session.get('application_data'), state='lodged')

        messages.success(request, 'The application was successfully lodged.')

        return redirect('applications:applications')
