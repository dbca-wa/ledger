from rest_framework.exceptions import APIException,PermissionDenied

class ReferralNotAuthorized(PermissionDenied):
    default_detail = 'You are not authorised to work on this referral'
    default_code = 'referral_not_authorized'

class ApplicationNotAuthorized(PermissionDenied):
    default_detail = 'You are not authorised to work on this application'
    default_code = 'application_not_authorized'

class ReferralCanNotSend(PermissionDenied):
    default_detail = 'You can only send referrals sent from an assessor'
    default_code = 'referral_level_send_unauthorized'

class ApplicationReferralCannotBeSent(PermissionDenied):
    default_detail = 'Referrals can only be sent if it is in the right processing status'
    default_code = 'application_referral_cannot_be_sent'

class ApplicationNotComplete(APIException):
    status_code = 400
    default_detail = 'The application is not complete'
    default_code = 'application_incoplete'

class ApplicationMissingFields(APIException):
    status_code = 400
    default_detail = 'The application has missing required fields'
    default_code = 'application_missing_fields'

class BindApplicationException(Exception):
    pass