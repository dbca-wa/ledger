from __future__ import unicode_literals
import datetime

from django.utils import six
from django.test import TestCase

from wildlifelicensing.apps.returns.tests import helpers
from wildlifelicensing.apps.returns.tests.helpers import BASE_CONSTRAINTS, clone, BASE_FIELD, REQUIRED_CONSTRAINTS
from wildlifelicensing.apps.returns.utils_schema import SchemaConstraints, FieldSchemaError, SchemaField, Schema


class TestSchemaConstraints(TestCase):
    def test_none_or_empty(self):
        """
        None or empty is accepted
        """
        self.assertEquals({}, SchemaConstraints(None).data)
        self.assertEquals({}, SchemaConstraints({}).data)

    def test_required_property(self):
        # no constraints -> require = False
        self.assertFalse(SchemaConstraints(None).required)
        cts = clone(BASE_CONSTRAINTS)
        self.assertFalse(cts['required'])
        self.assertFalse(SchemaConstraints(cts).required)

        cts = clone(BASE_CONSTRAINTS)
        cts['required'] = True
        self.assertTrue(cts['required'])
        self.assertTrue(SchemaConstraints(cts).required)

    def test_get_method(self):
        """
        test that the SchemaField has the dict-like get('key', default)
        """
        cts = clone(BASE_CONSTRAINTS)
        sch = SchemaConstraints(cts)
        self.assertTrue(hasattr(sch, 'get'))
        self.assertEquals(cts.get('required'), sch.get('required'))
        self.assertEquals(cts.get('constraints'), sch.get('constraints'))
        self.assertEquals(None, sch.get('bad_keys'))
        self.assertEquals('default', sch.get('bad_keys', 'default'))


class TestSchemaField(TestCase):
    def setUp(self):
        self.base_field = clone(BASE_FIELD)

    def test_name_mandatory(self):
        """
        A schema field without name should throw an exception
        """
        field = self.base_field
        del field['name']
        with self.assertRaises(FieldSchemaError):
            SchemaField(field)
        # no blank
        field = self.base_field
        field['name'] = ''
        with self.assertRaises(FieldSchemaError):
            SchemaField(field)

    def test_get_method(self):
        """
        test that the SchemaField has the dict-like get('key', default)
        """
        field = self.base_field
        sch = SchemaField(field)
        self.assertTrue(hasattr(sch, 'get'))
        self.assertEquals(field.get('Name'), sch.get('Name'))
        self.assertEquals(field.get('constraints'), sch.get('constraints'))
        self.assertEquals(None, sch.get('bad_keys'))
        self.assertEquals('default', sch.get('bad_keys', 'default'))

    def test_column_name(self):
        """
        'column_name' is a property that is equal to name
        """
        field = self.base_field
        sch = SchemaField(field)
        self.assertEquals(sch.name, sch.column_name)
        self.assertNotEqual(sch.column_name, sch.title)

    def test_constraints(self):
        """
        test that the constraints property returned a SchemaConstraints
        """
        self.assertIsInstance(SchemaField(BASE_FIELD).constraints, SchemaConstraints)


class TestSchemaFieldCast(TestCase):
    def setUp(self):
        self.base_field_descriptor = clone(BASE_FIELD)

    def test_boolean(self):
        true_values = [True, 'True', 'true', 'YES', 'yes', 'y', 't', '1', 1]
        false_values = [False, 'FALSE', 'false', 'NO', 'no', 'n', 'f', '0', 0]
        wrong_values = [2, 3, 'FLSE', 'flse', 'NON', 'oui', 'maybe', 'not sure']
        descriptor = self.base_field_descriptor
        descriptor['type'] = 'boolean'
        # only 'default' format
        descriptor['format'] = 'default'
        f = SchemaField(descriptor)
        for v in true_values:
            self.assertTrue(f.cast(v))
        for v in false_values:
            self.assertFalse(f.cast(v))
        for v in wrong_values:
            with self.assertRaises(Exception):
                f.cast(v)

    def test_date(self):
        descriptor = clone(BASE_FIELD)
        descriptor['type'] = 'date'
        # 'default' format = ISO
        descriptor['format'] = 'default'
        f = SchemaField(descriptor)
        valid_values = ['2016-07-29']
        for v in valid_values:
            date = f.cast(v)
            self.assertIsInstance(date, datetime.date)
            self.assertEqual(datetime.date(2016, 7, 29), date)
        invalid_value = ['29/07/2016', '07/29/2016', '2016-07-29 15:28:37']
        for v in invalid_value:
            with self.assertRaises(Exception):
                f.cast(v)

        # format='any'. 
        # The main problem is to be sure that a dd/mm/yyyy is not interpreted as mm/dd/yyyy
        descriptor['format'] = 'any'
        f = SchemaField(descriptor)
        valid_values = [
            '2016-07-10',
            '10/07/2016',
            '10/07/16',
            '2016-07-10 15:28:37',
            '10-July-2016',
            '10-JUlY-16',
            '10-07-2016',
            '10-07-16'
        ]
        expected_date = datetime.date(2016, 7, 10)
        for v in valid_values:
            date = f.cast(v)
            self.assertIsInstance(date, datetime.date)
            self.assertEqual(expected_date, date)
        invalid_value = ['djskdj']
        for v in invalid_value:
            with self.assertRaises(Exception):
                f.cast(v)

    def test_date_custom_format(self):
        format_ = 'fmt:%d %b %y'  # ex 30 Nov 14
        descriptor = {
            'name': 'Date with fmt',
            'type': 'date',
            'format': format_
        }
        field = SchemaField(descriptor)
        value = '30 Nov 14'
        self.assertEqual(field.cast(value), datetime.date(2014, 11, 30))

        format_ = 'fmt:%d/%m/%Y'
        descriptor = {
            'name': 'Date with fmt',
            'type': 'date',
            'format': format_
        }
        field = SchemaField(descriptor)
        value = '12/07/2016'
        value = field.cast(value)
        self.assertEqual(type(value), datetime.date)
        self.assertEqual(value, datetime.date(2016, 7, 12))

    def test_string(self):
        # test that a blank string '' is not accepted when the field is required
        null_values = ['null', 'none', 'nil', 'nan', '-', '']
        desc = clone(BASE_FIELD)
        desc['type'] = 'string'
        desc['constraints'] = clone(REQUIRED_CONSTRAINTS)
        f = SchemaField(desc)
        for v in null_values:
            with self.assertRaises(Exception):
                f.cast(v)

        # test non unicode (python 2)
        value = 'not unicode'
        self.assertIsInstance(f.cast(value), six.text_type)
        self.assertEqual(f.cast(value), value)

    def test_datetime_any(self):
        """
        test datetime field with 'any' format
        :return:
        """
        descriptor = clone(BASE_FIELD)
        descriptor['type'] = 'datetime'
        # format='any'.
        # The main problem is to be sure that a dd/mm/yyyy is not interpreted as mm/dd/yyyy
        descriptor['format'] = 'any'
        f = SchemaField(descriptor)
        valid_values = [
            '2016-07-10 13:55:00',
            '10/07/2016 13:55',
            '10/07/16 1:55 pm',
            '2016-07-10 13:55:00',
            '10-July-2016 13:55:00',
            '10-JUlY-16 13:55:00',
            '10-07-2016 13:55:00',
            '10-07-16 13:55:00'
        ]
        expected_dt = datetime.datetime(2016, 7, 10, 13, 55, 00)
        for v in valid_values:
            dt = f.cast(v)
            self.assertIsInstance(dt, datetime.datetime)
            self.assertEqual(expected_dt, dt)
        invalid_value = ['djskdj']
        for v in invalid_value:
            with self.assertRaises(Exception):
                f.cast(v)


class TestSchemaFieldValidation(TestCase):

    def test_enums(self):
        """
        Test that if a field has an enum constraint and if the data doesn't fit the error message should give the list
        of the possible values.
        :return:
        """
        descriptor = {
            "name": "Enum",
            "title": "Test Enum message",
            "type": "string",
            "format": "default",
            "constraints": {
                "required": False,
                "enum": ["val1", "val2", "val3"]
            }
        }
        f = SchemaField(descriptor)
        valid_values = ['val1', 'val2', 'val3', '']  # non required should accept blank
        for v in valid_values:
            self.assertIsNone(f.validation_error(v))

        wrong_values = ['xxx']
        for v in wrong_values:
            msg = f.validation_error(v)
            self.assertTrue(msg)
            # test that the error message contains each of the enum values.
            for vv in f.constraints['enum']:
                self.assertTrue(msg.find(vv) >= 0)


class TestSpeciesField(TestCase):
    def test_no_species(self):
        descriptor = clone(helpers.GENERIC_SCHEMA)
        sch = Schema(descriptor)
        # no species field
        self.assertFalse(sch.species_fields)

    def test_species_by_field_name(self):
        """
        A previous implementation supported species field detection by just the field name.
        Not anymore
        :return:
        """
        names = ['species name', 'Species Name', 'SPECIES_NAME', 'species_Name']
        for name in names:
            descriptor = clone(helpers.GENERIC_SCHEMA)
            sch = Schema(descriptor)
            # no species field
            self.assertFalse(sch.species_fields)
            # add a field named name
            field = clone(BASE_FIELD)
            field['name'] = name
            descriptor['fields'].append(field)
            sch = Schema(descriptor)
            self.assertEqual(0, len(sch.species_fields))

    def test_species_by_wl_tag(self):
        # adding a wl species tag to a field turns it into a species field (whatever its name)
        descriptor = clone(helpers.GENERIC_SCHEMA)
        sch = Schema(descriptor)
        # no species field
        self.assertFalse(sch.species_fields)
        # tag
        field = descriptor['fields'][0]
        field['wl'] = {
            'type': 'species'
        }
        sch = Schema(descriptor)
        self.assertEqual(1, len(sch.species_fields))
        self.assertEquals(field['name'], sch.species_fields[0].name)


class TestLatLongEastingNorthingCase(TestCase):
    """
    Test the conditional requirement between long/lat and easting/northing.
    One or the other must be required.
    """

    def setUp(self):
        self.schema_descriptor = {
            "fields": [
                {
                    "type": "string",
                    "name": "DATUM",
                    "constraints": {
                        "required": True,
                        "enum": ["GDA94", "WGS84", "AGD84", "AGD66"]
                    },
                },
                {
                    "type": "number",
                    "name": "LATITUDE",
                    "constraints": {
                        "minimum": -60.0,
                        "maximum": 0,
                        "required": True
                    }
                },
                {
                    "type": "number",
                    "name": "LONGITUDE",
                    "constraints": {
                        "minimum": 80.0,
                        "maximum": 170.0,
                        "required": True
                    }
                },
                {
                    "type": "number",
                    "name": "ZONE",
                    "constraints": {
                        "required": True,
                        "enum": [49, 50, 51, 52]
                    }
                },
                {
                    "type": "number",
                    "name": "EASTING",
                    "constraints": {
                        "required": True,
                    }
                },
                {
                    "type": "number",
                    "name": "NORTHING",
                    "constraints": {
                        "required": True,
                    }
                },
            ]
        }
        self.schema = Schema(self.schema_descriptor)
        self.assertTrue(self.schema.is_lat_long_easting_northing_schema())

    def test_lat_long_only(self):
        """
        Lat/Long + datum should not generate an error
        :return:
        """
        data = {
            "DATUM": "WGS84",
            "LATITUDE": -32,
            "LONGITUDE": 116,
            "EASTING": None,
            "NORTHING": None,
            "ZONE": None
        }
        self.assertTrue(self.schema.is_row_valid(data))

        # datum always required
        data = {
            "DATUM": None,
            "LATITUDE": -32,
            "LONGITUDE": 116,
            "EASTING": None,
            "NORTHING": None,
            "ZONE": None
        }
        self.assertFalse(self.schema.is_row_valid(data))
        errors = self.schema.get_error_fields(data)
        self.assertEqual(len(errors), 1)
        self.assertEqual('DATUM', errors[0][0])

    def test_east_north_only(self):
        """
        Northing/Easting + Datum + Zone should be valid
        :return:
        """
        data = {
            "DATUM": "WGS84",
            "LATITUDE": None,
            "LONGITUDE": None,
            "EASTING": 123456,
            "NORTHING": 654321,
            "ZONE": 50
        }
        self.assertTrue(self.schema.is_row_valid(data))

        # datum always required
        data = {
            "DATUM": None,
            "LATITUDE": None,
            "LONGITUDE": None,
            "EASTING": 123456,
            "NORTHING": 654321,
            "ZONE": 50
        }
        self.assertFalse(self.schema.is_row_valid(data))
        errors = self.schema.get_error_fields(data)
        self.assertEqual(len(errors), 1)
        self.assertEqual('DATUM', errors[0][0])

        # ZONE always required
        data = {
            "DATUM": "WGS84",
            "LATITUDE": None,
            "LONGITUDE": None,
            "EASTING": 123456,
            "NORTHING": 654321,
            "ZONE": ''
        }
        self.assertFalse(self.schema.is_row_valid(data))
        errors = self.schema.get_error_fields(data)
        self.assertEqual(len(errors), 1)
        self.assertEqual('ZONE', errors[0][0])

    def test_no_lat_long_and_no_east_north(self):
        data = {
            "DATUM": "WGS84",
            "LATITUDE": '',
            "LONGITUDE": '',
            "EASTING": None,
            "NORTHING": None,
            "ZONE": 50
        }
        self.assertFalse(self.schema.is_row_valid(data))
        error_fields = [e[0] for e in self.schema.get_error_fields(data)]
        self.assertTrue('LATITUDE' in error_fields)
        self.assertTrue('LONGITUDE' in error_fields)
        self.assertTrue('EASTING' in error_fields)
        self.assertTrue('NORTHING' in error_fields)

    def test_half_baked_data(self):
        """
        Missing either lat or long ot east or north
        :return:
        """
        data = {
            "DATUM": "WGS84",
            "LATITUDE": -32,
            "LONGITUDE": None,
            "EASTING": None,
            "NORTHING": None,
            "ZONE": 50
        }
        self.assertFalse(self.schema.is_row_valid(data))
        error_fields = [e[0] for e in self.schema.get_error_fields(data)]
        self.assertFalse('LATITUDE' in error_fields)
        self.assertTrue('NORTHING' in error_fields)
        self.assertTrue('LONGITUDE' in error_fields)
        self.assertTrue('EASTING' in error_fields)

        data = {
            "DATUM": "WGS84",
            "LATITUDE": None,
            "LONGITUDE": 115,
            "EASTING": None,
            "NORTHING": None,
            "ZONE": 50
        }
        self.assertFalse(self.schema.is_row_valid(data))
        error_fields = [e[0] for e in self.schema.get_error_fields(data)]
        self.assertFalse('LONGITUDE' in error_fields)
        self.assertTrue('EASTING' in error_fields)
        self.assertTrue('LATITUDE' in error_fields)
        self.assertTrue('NORTHING' in error_fields)

        data = {
            "DATUM": "WGS84",
            "LATITUDE": None,
            "LONGITUDE": None,
            "EASTING": 123456,
            "NORTHING": None,
            "ZONE": 50
        }
        self.assertFalse(self.schema.is_row_valid(data))
        error_fields = [e[0] for e in self.schema.get_error_fields(data)]
        self.assertTrue('LONGITUDE' in error_fields)
        self.assertFalse('EASTING' in error_fields)
        self.assertTrue('LATITUDE' in error_fields)
        self.assertTrue('NORTHING' in error_fields)

        data = {
            "DATUM": "WGS84",
            "LATITUDE": None,
            "LONGITUDE": None,
            "EASTING": None,
            "NORTHING": 645321,
            "ZONE": 50
        }
        self.assertFalse(self.schema.is_row_valid(data))
        error_fields = [e[0] for e in self.schema.get_error_fields(data)]
        self.assertFalse('NORTHING' in error_fields)
        self.assertTrue('LATITUDE' in error_fields)
        self.assertTrue('LONGITUDE' in error_fields)
        self.assertTrue('EASTING' in error_fields)

    def test_mixed_data(self):
        """
        Test that data that mixed lat/long and noth/east are not valid
        E.g provide lat but not long and provide easting but not northing
        :return:
        """
        data = {
            "DATUM": "WGS84",
            "LATITUDE": -32,
            "LONGITUDE": None,
            "EASTING": 12345,
            "NORTHING": None,
            "ZONE": 50
        }
        self.assertFalse(self.schema.is_row_valid(data))
        error_fields = [e[0] for e in self.schema.get_error_fields(data)]
        self.assertFalse('LATITUDE' in error_fields)
        self.assertFalse('EASTING' in error_fields)
        self.assertTrue('LONGITUDE' in error_fields)
        self.assertTrue('NORTHING' in error_fields)
