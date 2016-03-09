from django.views.generic.edit import FormView
from django.shortcuts import render

from forms import ApplicationForm


class ApplicationView(FormView):
    template_name = 'application.html'
    form_class = ApplicationForm

    def get(self, request, *args, **kwargs):
        return super(ApplicationView, self).get(*args, **kwargs)