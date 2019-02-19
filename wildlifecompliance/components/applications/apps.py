from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ApplicationsConfig(AppConfig):
    name = 'wildlifecompliance.components.applications'
    verbose_name = _('applicationss')

    def ready(self):
        import wildlifecompliance.components.applications.signals
