from django.apps import AppConfig
# from django.utils.translation import ugettext_lazy as _
from django.utils.translation import gettext_lazy as _


class PromotionsConfig(AppConfig):
    label = 'promotions_app'
    name = 'oscar.apps.promotions'
    verbose_name = _('Promotions')
