from rest_framework.exceptions import APIException,PermissionDenied

class ReferralNotAuthorized(PermissionDenied):
    default_detail = 'You are not authorised to work on this referral'
    default_code = 'referral_not_authorized'

class ProposalNotAuthorized(PermissionDenied):
    default_detail = 'You are not authorised to work on this proposal'
    default_code = 'proposal_not_authorized'

class ReferralCanNotSend(PermissionDenied):
    default_detail = 'You can only send referrals sent from an assessor'
    default_code = 'referral_level_send_unauthorized'
