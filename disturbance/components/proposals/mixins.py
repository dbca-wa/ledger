from django.core.exceptions import PermissionDenied

class ReferralOwnerMixin(object):
    
    def check_owner(self, user):
        return self.get_object().referral == user

    def dispatch(self, request, *args, **kwargs):
        if not self.check_owner(request.user):    
            raise PermissionDenied
        return super(ReferralMixin, self).dispatch(request, *args, **kwargs)
