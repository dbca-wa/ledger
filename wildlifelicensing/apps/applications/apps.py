from __future__ import unicode_literals

from django.apps import AppConfig
from mock import self


class ApplicationsConfig(AppConfig):
    name = 'wildlifelicensing.apps.applications'
    verbose_name = 'applications'

    run_once = False

    def ready(self):
        if not self.run_once:
            import signals
        
        self.run_once = True
