from django.core.exceptions import PermissionDenied

class InvoiceOwnerMixin(object):
    
    def belongs_to(self,user, group_name):
        """
        Check if the user belongs to the given group.
        :param user:
        :param group_name:
        :return:
        """
        return user.groups.filter(name=group_name).exists()
    

    def is_payment_admin(self,user):
        return user.is_authenticated() and (self.belongs_to(user, 'Payments Officers') or user.is_superuser)

    def check_owner(self, user):
        return self.get_object().order.user == user or self.is_payment_admin(user)

    def dispatch(self, request, *args, **kwargs):
        if not self.check_owner(request.user):    
            raise PermissionDenied
        return super(InvoiceOwnerMixin, self).dispatch(request, *args, **kwargs)
