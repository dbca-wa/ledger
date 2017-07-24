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

class ProposalReferralCannotBeSent(PermissionDenied):
    default_detail = 'Referrals can only be sent if it is in the right processing status'
    default_code = 'proposal_referral_cannot_be_sent'
