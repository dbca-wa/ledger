from datetime import timedelta


def create_returns_due_dates(start_date, end_date, monthly_frequency):
    dates = []
    if monthly_frequency < 0:
        dates.append(end_date)
    else:
        months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month

        num_returns = months / monthly_frequency

        for return_num in range(1, num_returns + 1):
            dates.append(start_date + timedelta(days=(return_num * monthly_frequency * 365) / 12))

    return dates
