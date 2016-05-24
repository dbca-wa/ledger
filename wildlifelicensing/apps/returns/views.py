from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404

from wildlifelicensing.apps.main.mixins import OfficerRequiredMixin, OfficerOrCustomerRequiredMixin
from wildlifelicensing.apps.returns.models import ReturnType


class EnterReturnView(OfficerOrCustomerRequiredMixin, TemplateView):
    template_name = 'wl/enter_return.html'
    login_url = '/'

    def get_context_data(self, **kwargs):
        kwargs['return_type'] = get_object_or_404(ReturnType, code=self.args[0])

        return super(EnterReturnView, self).get_context_data(**kwargs)


class CurateReturnView(OfficerRequiredMixin, TemplateView):
    template_name = 'wl/curate_return.html'
    login_url = '/'
