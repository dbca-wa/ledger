from rest_framework.exceptions import APIException,PermissionDenied

class ReferralNotAuthorized(PermissionDenied):
    default_detail = 'You are not authorised to work on this referral'
    default_code = 'referral_not_authorized'
