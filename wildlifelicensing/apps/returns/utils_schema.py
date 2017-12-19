from __future__ import absolute_import, unicode_literals, print_function, division
from future.utils import raise_with_traceback

import json
import re

from dateutil.parser import parse as date_parse

# TODO: fix the deprecation of SchemaModel. Use jsontableschema.model.Schema, but there is a problem (see below)
from jsontableschema.model import SchemaModel
from jsontableschema import types
from jsontableschema.exceptions import InvalidDateType

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.writer.write_only import WriteOnlyCell
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible

from wildlifelicensing.apps.main.excel import is_blank_value

COLUMN_HEADER_FONT = Font(bold=True)

YYYY_MM_DD_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}')


class FieldSchemaError(Exception):
    pass


def parse_datetime_day_first(value):
    """
    use the dateutil.parse() to parse a date/datetime with the date first (dd/mm/yyyy) (not month first mm/dd/yyyy)
    in case of ambiguity
    :param value:
    :return:
    """
    # there's a 'bug' in dateutil.parser.parse (2.5.3). If you are using
    # dayfirst=True. It will parse YYYY-MM-DD as YYYY-DD-MM !!
    # https://github.com/dateutil/dateutil/issues/268
    dayfirst = not YYYY_MM_DD_REGEX.match(value)
    return date_parse(value, dayfirst=dayfirst)


class DayFirstDateType(types.DateType):
    """
    Extend the jsontableschema DateType which use the mm/dd/yyyy date model for the 'any' format
    to use dd/mm/yyyy.
    """

    def cast_any(self, value, fmt=None):
        if isinstance(value, self.python_type):
            return value
        try:
            return parse_datetime_day_first(value).date()
        except (TypeError, ValueError) as e:
            raise_with_traceback(InvalidDateType(e))


class DayFirstDateTimeType(types.DateTimeType):
    """
    Extend the jsontableschema DateType which use the mm/dd/yyyy date model for the 'any' format
    to use dd/mm/yyyy
    """

    def cast_any(self, value, fmt=None):
        if isinstance(value, self.python_type):
            return value
        try:
            return parse_datetime_day_first(value)
        except (TypeError, ValueError) as e:
            raise_with_traceback(InvalidDateType(e))


class NotBlankStringType(types.StringType):
    """
    The default StringType accepts empty string when required = True
    """
    null_values = ['null', 'none', 'nil', 'nan', '-', '']


@python_2_unicode_compatible
class WLSchema:
    """
    The utility class for the wildlife licensing data within a schema field
    Use to tag a filed to be a species field
    {
      name: "...."
      constraints: ....
      wl: {
                type: "species"
                speciesType: 'fauna'|'flora'|'all'
          }
    }
    """
    SPECIES_TYPE_NAME = 'species'
    SPECIES_TYPE_FLORA_NAME = 'flora'
    SPECIES_TYPE_FAUNA_NAME = 'fauna'

    def __init__(self, data):
        self.data = data or {}

    # implement some dict like methods
    def __getitem__(self, item):
        return self.data.__getitem__(item)

    def __str__(self):
        return "WLSchema: {}".format(self.data)

    @property
    def type(self):
        return self.get('type')

    @property
    def species_type(self):
        return self.get('speciesType')

    def get(self, k, d=None):
        return self.data.get(k, d)

    def is_species_type(self):
        return self.type == self.SPECIES_TYPE_NAME


@python_2_unicode_compatible
class SchemaField:
    """
    Utility class for a field in a schema.
    It uses the schema types of
    https://github.com/frictionlessdata/jsontableschema-py#types
    for validation.
    """
    # For most of the type we use the jsontableschema ones
    # TODO: SchemaModel is deprecated in favor of of jsontableschema.schema.Schema but there's no _type_map!
    BASE_TYPE_MAP = SchemaModel._type_map()
    # except for anything date.
    BASE_TYPE_MAP['date'] = DayFirstDateType
    BASE_TYPE_MAP['datetime'] = DayFirstDateTimeType
    # and string
    BASE_TYPE_MAP['string'] = NotBlankStringType

    WL_TYPE_MAP = {
    }

    def __init__(self, data):
        self.data = data
        self.name = self.data.get('name')
        # We want to throw an exception if there is no name
        if not self.name:
            raise FieldSchemaError("A field without a name: {}".format(json.dumps(data)))
        # wl specific
        self.wl = WLSchema(self.data.get('wl'))
        # set the type: wl type as precedence
        type_class = self.WL_TYPE_MAP.get(self.wl.type) or self.BASE_TYPE_MAP.get(self.data.get('type'))
        self.type = type_class(self.data)
        self.constraints = SchemaConstraints(self.data.get('constraints', {}))

    # implement some dict like methods
    def __getitem__(self, item):
        return self.data.__getitem__(item)

    def get(self, k, d=None):
        return self.data.get(k, d)

    @property
    def title(self):
        return self.data.get('title')

    @property
    def column_name(self):
        return self.name

    @property
    def required(self):
        return self.constraints.required

    @property
    def is_species(self):
        return self.wl.is_species_type()

    @property
    def species_type(self):
        result = None
        if self.is_species:
            return self.wl.species_type or 'all'
        return result

    def cast(self, value):
        """
        Returns a native Python object of the expected format. Will throw an exception
        if the value doesn't complies with any constraints. See for details:
        https://github.com/frictionlessdata/jsontableschema-py#types
        This method is mainly a helper for the validation_error
        :param value:
        :return:
        """
        if isinstance(value, six.string_types) and not isinstance(value, six.text_type):
            # the StringType accepts only unicode
            value = six.u(value)
        elif isinstance(value,six.integer_types):
            value = '{}'.format(value)
        return self.type.cast(value)

    def validate(self, value):
        return self.validation_error(value)

    def validation_error(self, value):
        """
        Return an error message if the value is not valid according to the schema.
        It relies on exception thrown by the 'cast1 method of Type method.
        :param value:
        :return: None if value is valid or an error message string
        """
        error = None
        # override the integer validation. The default message is a bit cryptic if there's an error casting a string
        # like '1.2' into an int.
        if isinstance(self.type, types.IntegerType):
            if not is_blank_value(value):
                not_integer = False
                try:
                    casted = self.cast(value)
                    # there's also the case where the case where a float 1.2 is successfully casted in 1
                    # (ex: int(1.2) = 1)
                    if str(casted) != str(value):
                        not_integer = True
                except Exception:
                    not_integer = True
                if not_integer:
                    return 'The field "{}" must be a whole number.'.format(self.name)
        try:
            self.cast(value)
        except Exception as e:
            error = "{}".format(e)
            # Override the default enum exception message to include all possible values
            if error.find('enum array') and self.constraints.enum:
                values = [str(v) for v in self.constraints.enum]
                error = "The value must be one the following: {}".format(values)
        return error

    def __str__(self):
        return '{}'.format(self.name)


class SchemaConstraints:
    """
    A helper class for a schema field constraints
    """

    def __init__(self, data):
        self.data = data or {}

    # implement some dict like methods
    def __getitem__(self, item):
        return self.data.__getitem__(item)

    def get(self, k, d=None):
        return self.data.get(k, d)

    @property
    def required(self):
        return self.get('required', False)

    @property
    def enum(self):
        return self.get('enum')


class Schema:
    """
    A utility class for schema.
    It uses internally an instance SchemaModel of the frictionless jsontableschema for help.
    https://github.com/frictionlessdata/jsontableschema-py#model
    """

    def __init__(self, schema):
        self.data = schema
        self.schema_model = SchemaModel(schema)
        self.fields = [SchemaField(f) for f in self.schema_model.fields]
        self.species_fields = self.find_species_fields(self)

    # implement some dict like methods
    def __getitem__(self, item):
        return self.data.__getitem__(item)

    def get(self, k, d=None):
        return self.data.get(k, d)

    @staticmethod
    def find_species_fields(schema):
        """
        Precedence Rules:
        1- Look for field of wl.type = 'species'
        :param schema: a dict descriptor or a Schema instance
        :return: an array of [SchemaField] or []
        """
        if not isinstance(schema, Schema):
            schema = Schema(schema)
        return [f for f in schema.fields if f.is_species]

    @property
    def headers(self):
        return self.field_names

    @property
    def field_names(self):
        return [f.name for f in self.fields]

    def get_field_by_mame(self, name, icase=False):
        if icase and name:
            name = name.lower()
        for f in self.fields:
            field_name = f.name.lower() if icase else f.name
            if field_name == name:
                return f
        return None

    def field_validation_error(self, field_name, value):
        field = self.get_field_by_mame(field_name)
        if field is not None:
            return field.validation_error(value)
        else:
            raise Exception("The field '{}' doesn't exists in the schema. Should be one of {}"
                            .format(field_name, self.field_names))

    def is_field_valid(self, field_name, value):
        return self.field_validation_error(field_name, value) is None

    def is_lat_long_easting_northing_schema(self):
        """
        True if there is a latitude, longitude, easting, northing, and zone field
        :return:
        """
        field_names = [name.lower() for name in self.field_names]
        return all([
            'latitude' in field_names,
            'longitude' in field_names,
            'easting' in field_names,
            'northing' in field_names,
            'zone' in field_names
        ])

    def post_validate_lat_long_easting_northing(self, field_validation):
        """
        We want conditional requirements: either lat/long or northing/easting.
        The goal is to remove the requirements on lat/long if we have east/north and vice versa.
        Rules:
        If lat and no northing remove northing error and zone error
        If northing and no latitude remove latitude error.
        If long and no easting remove easting error and zone error
        If easting and no longitude remove longitude error.
        :param field_validation: We expect that the data has been validated at the field level and the argument should be
        the result of this validation (see validate_row()).
        Expected format:
        {field_name: { 'value': value, 'error': None|msg}}
        :return:
        """
        if not self.is_lat_long_easting_northing_schema():
            return field_validation
        lat_validation = field_validation.get(self.get_field_by_mame('latitude', icase=True).name, {})
        north_validation = field_validation.get(self.get_field_by_mame('northing', icase=True).name, {})
        long_validation = field_validation.get(self.get_field_by_mame('longitude', icase=True).name, {})
        east_validation = field_validation.get(self.get_field_by_mame('easting', icase=True).name, {})
        zone_validation = field_validation.get(self.get_field_by_mame('zone', icase=True).name, {})
        if lat_validation.get('value') and long_validation.get('value'):
            if not north_validation.get('value'):
                north_validation['error'] = None
                zone_validation['error'] = None
            if not east_validation.get('value'):
                east_validation['error'] = None
                zone_validation['error'] = None
        if east_validation.get('value') and north_validation.get('value'):
            if not lat_validation.get('value'):
                lat_validation['error'] = None
            if not long_validation.get('value'):
                long_validation['error'] = None
        return field_validation

    def validate_row(self, row):
        """
        The row must be a dictionary or a list of key value
        :param row:
        :return: return a dictionary with an error added to the field
        {
            field_name: {
                value: value (as given)
                error: None or error message
        }
        """
        row = dict(row)
        result = {}
        # field validation
        for field_name, value in row.items():
            error = self.field_validation_error(field_name, value)
            result[field_name] = {
                'value': value,
                'error': error
            }
        # Special case for lat/long easting/northing
        if self.is_lat_long_easting_northing_schema():
            result = self.post_validate_lat_long_easting_northing(result)
        return result

    def rows_validator(self, rows):
        for row in rows:
            yield self.validate_row(row)

    def get_error_fields(self, row):
        """
        Return the field that does not validate
        :param row: a key value dict or tuple
        :return: [(field_name, {'value':value, 'error':error_string}]
        """
        validated_row = self.validate_row(row)
        errors = []
        for field, data in validated_row.items():
            if data.get('error'):
                errors.append((field, data))
        return errors

    def is_row_valid(self, row):
        return len(self.get_error_fields(row)) == 0

    def is_all_valid(self, rows):
        for row in rows:
            if not self.is_row_valid(row):
                return False
        return True


def create_return_template_workbook(return_type):
    wb = Workbook(write_only=True)
    for resource in return_type.resources:
        schema = Schema(resource.get('schema'))
        ws = wb.create_sheet()
        ws.title = resource.get('title', resource.get('name'))
        headers = []
        for header in schema.headers:
            cell = WriteOnlyCell(ws, value=header)
            cell.font = COLUMN_HEADER_FONT
            headers.append(cell)
        ws.append(headers)
    return wb
