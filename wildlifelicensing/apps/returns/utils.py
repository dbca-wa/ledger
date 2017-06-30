from datetime import date
from wildlifelicensing.apps.returns.models import Return
from dateutil.relativedelta import relativedelta

RETURN_STATUSES = dict(Return.STATUS_CHOICES)


def create_returns_due_dates(start_date, end_date, monthly_frequency):
    due_dates = []
    if monthly_frequency < 0:
        due_dates.append(end_date)
    else:
        count = 1
        delta = relativedelta(months=count*monthly_frequency)
        due_date = start_date + delta
        if due_date > end_date:
            # case where the first return due date is > end_date
            # treat it like a one off
            due_dates.append(end_date)
        else:
            count += 1
            while due_date <= end_date:
                due_dates.append(due_date)
                delta = relativedelta(months=count*monthly_frequency)
                due_date = start_date + delta
                count += 1
    return due_dates


def is_return_overdue(ret):
    status = ret.status
    return status in Return.CUSTOMER_EDITABLE_STATE and ret.due_date <= date.today()


def is_return_due_soon(ret):
    days_soon = 14
    status = ret.status
    return status in Return.CUSTOMER_EDITABLE_STATE and (ret.due_date - date.today()).days < days_soon or is_return_overdue(ret)


def format_return(instance, attrs):
    attrs['status'] = RETURN_STATUSES[attrs['status']]

    return attrs
