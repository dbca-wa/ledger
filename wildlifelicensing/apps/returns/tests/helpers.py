from datetime import date, timedelta

from wildlifelicensing.apps.returns.models import Return, ReturnType


def get_or_create_return_type(licence_type):
    return ReturnType.objects.get_or_create(licence_type=licence_type)[0]


def create_return(licence):
    return_type = get_or_create_return_type(licence.licence_type)

    return Return.objects.create(return_type=return_type, licence=licence, due_date=date.today() + timedelta(weeks=52),
                                 status='current')
