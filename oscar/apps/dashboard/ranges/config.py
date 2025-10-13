from django.apps import AppConfig
# from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _


class RangesDashboardConfig(AppConfig):
    label = 'ranges_dashboard'
    name = 'oscar.apps.dashboard.ranges'
    verbose_name = _('Ranges dashboard')
