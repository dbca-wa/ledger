from __future__ import unicode_literals

from django.apps import AppConfig


class ReturnsConfig(AppConfig):
    name = 'wildlifelicensing.apps.returns'
    label = 'wl_returns'
    verbose_name = 'returns'

    run_once = False

    def ready(self):
        if not self.run_once:
            import signals

        self.run_once = True
