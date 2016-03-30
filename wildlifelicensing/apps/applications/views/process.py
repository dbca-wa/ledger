from django.views.generic import TemplateView


class ProcessView(TemplateView):
    template_name = 'wl/process/process_app.html'
