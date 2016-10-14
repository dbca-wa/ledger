from jsontableschema.model import SchemaModel
from jsontableschema import types
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.writer.write_only import WriteOnlyCell
from django.utils import six
from django.utils.encoding import python_2_unicode_compatible

from wildlifelicensing.apps.main.excel import is_blank_value

COLUMN_HEADER_FONT = Font(bold=True)


@python_2_unicode_compatible
class SchemaField:
    """
    Utility class for a field in a schema.
    It uses the schema types of
    https://github.com/frictionlessdata/jsontableschema-py#types
    for validation.
    """

    def __init__(self, data):
        self.data = data
        self.name = data['name']  # We want to throw an exception if there is no name
        # use of jsontableschema.types to help constraint validation
        self.type = SchemaModel._type_map()[data.get('type')](data)

    @property
    def column_name(self):
        return self.name

    @property
    def constraints(self):
        return self.data.get('constraints', {})

    @property
    def required(self):
        return self.constraints.get('required', False)

    def cast(self, value):
        """
        Returns a native Python object of the expected format. Will throw an exception
        if the value doesn't complies with any constraints. See for details:
        https://github.com/frictionlessdata/jsontableschema-py#types
        This method is mainly a helper for the validation_error
        :param value:
        :return:
        """
        if is_blank_value(value):
            # must do that because an empty string is considered as valid even if required by the StringType
            value = None
        if isinstance(value, six.string_types) and not isinstance(value, six.text_type):
            # the StringType accepts only unicode
            value = six.u(value)
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
            error = e.message
        return error

    def __str__(self):
        return '{}'.format(self.name)


class Schema:
    """
    A utility class for schema.
    It uses internally an instance SchemaModel of the frictionless jsontableschema for help.
    https://github.com/frictionlessdata/jsontableschema-py#model
    """

    def __init__(self, schema):
        self.schema_model = SchemaModel(schema)
        self.fields = [SchemaField(f) for f in self.schema_model.fields]

    @property
    def headers(self):
        return self.field_names

    @property
    def field_names(self):
        return [f.name for f in self.fields]

    def get_field_by_mame(self, name):
        for f in self.fields:
            if f.name == name:
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
        for field_name, value in row.items():
            error = self.field_validation_error(field_name, value)
            result[field_name] = {
                'value': value,
                'error': error
            }
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
