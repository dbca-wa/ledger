from __future__ import unicode_literals

from django.apps import AppConfig

class DisturbanceConfig(AppConfig):
    name = 'disturbance'

    run_once = False
    def ready(self):
        if not self.run_once:
            from disturbance.components.organisations import signals
            from disturbance.components.proposals import signals

        self.run_once = True
