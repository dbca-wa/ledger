import json
import os

from django.views.generic.base import TemplateView
from django.shortcuts import render_to_response


class ApplicationView(TemplateView):
    template_name = 'application.html'

    def get(self, request, *args, **kwargs):
        with open('%s/json/%s.json' % (os.path.abspath(os.path.dirname(__file__)), args[0])) as data_file:
            form_stucture = json.load(data_file)

        return render_to_response(self.template_name, {'structure': form_stucture})
