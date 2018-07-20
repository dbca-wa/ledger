from rest_framework.permissions import BasePermission
from mooring.helpers import is_officer, is_customer


# REST permissions
class OfficerPermission(BasePermission):
    def has_permission(self, request, view):
        return is_officer(request.user)

class PaymentCallbackPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return is_officer(request.user)
