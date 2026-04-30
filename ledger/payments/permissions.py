from rest_framework.permissions import BasePermission
from ledger.payments import helpers

class PaymentAdminPermission(BasePermission):

    def has_permission(self, request, view):
        return helpers.is_payment_admin(request.user)