from django.views.generic.edit import FormView
from django.shortcuts import render

from forms import ApplicationForm, Regulation17ApplicationForm


class ApplicationView(FormView):
    template_name = 'application.html'
    form_class = ApplicationForm

    def get(self, request, *args, **kwargs):
        if args[0] == 'reg17':
            self.form_class = Regulation17ApplicationForm

        return super(ApplicationView, self).get(*args, **kwargs)
