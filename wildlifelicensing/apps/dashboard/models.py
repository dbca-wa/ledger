from __future__ import unicode_literals
import random

from django.db import models

DATA_SAMPLES = {
    'dates': ['2016-01-01', '2015-12-11', '2015-04-04', '2015-01-30', '2017-12-24'],
    'customers': ['Serge Le Breton', 'Pauline Goodreid', 'Paul Gioia', 'Graham Thompson', 'Tony Prior'],
    'statusApplication': ['pending', 'draft', 'issued'],
    'licenseTypes': ['reg3', 'reg17', 'reg40', 'reg666'],
    'statusLicense': ['pending', 'granted', 'refused', 'cancelled']
}


def _sample(_list):
    index = random.sample(range(len(_list)), 1)[0]
    return _list[index]


def generate_mock_data(nb_rows=30):
    result = {
        'applications': [],
        'licenses': [],
        'returns': []
    }
    for i in range(nb_rows):
        result['applications'].append({
            'license_type': _sample(DATA_SAMPLES['licenseTypes']),
            'customer': _sample(DATA_SAMPLES['customers']),
            'date': _sample(DATA_SAMPLES['dates']),
            'status': _sample(DATA_SAMPLES['statusApplication'])
        })
        _license = {
            'license_type': _sample(DATA_SAMPLES['licenseTypes']),
            'customer': _sample(DATA_SAMPLES['customers']),
            'issue_date': _sample(DATA_SAMPLES['dates']),
            'expire_date': _sample(DATA_SAMPLES['dates']),
            'status': _sample(DATA_SAMPLES['statusLicense'])
        }
        _license['license_no'] = _license['license_type'] + '-' + str(random.randint(1, 100))
        result['licenses'].append(_license)

        _return = {
            'license_type': _sample(DATA_SAMPLES['licenseTypes']),
            'customer': _sample(DATA_SAMPLES['customers']),
            'due_date': _sample(DATA_SAMPLES['dates']),
            'status': _sample(DATA_SAMPLES['statusApplication'])
        }
        _return['license_no'] = _return['license_type'] + '-' + str(random.randint(1, 100))
        result['returns'].append(_return)

    return result
