import copy
from datetime import date, timedelta

from wildlifelicensing.apps.returns.models import Return, ReturnType


def clone(descriptor):
    return copy.deepcopy(descriptor)


BASE_CONSTRAINTS = {
    "required": False
}

NOT_REQUIRED_CONSTRAINTS = {
    "required": False
}

REQUIRED_CONSTRAINTS = {
    "required": True
}

BASE_FIELD = {
    "name": "Name",
    "tile": "Title",
    "type": "string",
    "format": "default",
    "constraints": clone(BASE_CONSTRAINTS)
}

GENERIC_SCHEMA = {
    "fields": [
        clone(BASE_FIELD)
    ]
}

GENERIC_DATA_PACKAGE = {
    "name": "test",
    "resources": [
        {
            "name": "test",
            "format": "CSV",
            "title": "test",
            "bytes": 0,
            "mediatype": "text/csv",
            "path": "test.csv",
            "schema": clone(GENERIC_SCHEMA)
        }
    ],
    "title": "Test"
}

SPECIES_NAME_FIELD = {
    "name": "Species Name",
    "type": "string",
    "format": "default",
    "constraints": {
        "required": True
    },
    "wl": {
        "type": "species"
    }
}

LAT_LONG_OBSERVATION_SCHEMA = {
    "fields": [
        {
            "name": "Observation Date",
            "type": "date",
            "format": "any",
            "constraints": {
                "required": True,
            }
        },
        {
            "name": "Latitude",
            "type": "number",
            "format": "default",
            "constraints": {
                "required": True,
                "minimum": -90.0,
                "maximum": 90.0,
            }
        },
        {
            "name": "Longitude",
            "type": "number",
            "format": "default",
            "constraints": {
                "required": True,
                "minimum": -180.0,
                "maximum": 180.0,
            }
        },
    ]
}

SPECIES_SCHEMA = clone(LAT_LONG_OBSERVATION_SCHEMA)
SPECIES_SCHEMA['fields'].append(clone(SPECIES_NAME_FIELD))

SPECIES_DATA_PACKAGE = clone(GENERIC_DATA_PACKAGE)
SPECIES_DATA_PACKAGE['resources'][0]['schema'] = clone(SPECIES_SCHEMA)


def get_or_create_return_type(licence_type):
    return ReturnType.objects.get_or_create(licence_type=licence_type)[0]


def create_return(licence):
    return_type = get_or_create_return_type(licence.licence_type)

    return Return.objects.create(return_type=return_type, licence=licence, due_date=date.today() + timedelta(weeks=52),
                                 status='current')
