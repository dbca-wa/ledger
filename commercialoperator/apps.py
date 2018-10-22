from __future__ import unicode_literals

from django.apps import AppConfig

class CommercialOperatorConfig(AppConfig):
    name = 'commercialoperator'

    run_once = False
    def ready(self):
        if not self.run_once:
            from commercialoperator.components.organisations import signals
            from commercialoperator.components.proposals import signals

        self.run_once = True
