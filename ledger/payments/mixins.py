from django.core.exceptions import PermissionDenied

from ledger.payments import helpers

class InvoiceOwnerMixin(object):
    
    def belongs_to(self, user, group_name):
        return helpers.belongs_to(user, group_name)

    def is_payment_admin(self,user):
        return helpers.is_payment_admin(user)

    def check_owner(self, user):
        return self.get_object().order.user == user or self.is_payment_admin(user)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_owner(request.user):    
            raise PermissionDenied
        return super(InvoiceOwnerMixin, self).dispatch(request, *args, **kwargs)
