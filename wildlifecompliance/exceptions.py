from rest_framework.exceptions import APIException,PermissionDenied


class ApplicationNotAuthorized(PermissionDenied):
    default_detail = 'You are not authorised to work on this application'
    default_code = 'application_not_authorized'

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