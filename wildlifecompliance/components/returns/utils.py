from wildlifecompliance.components.returns.models import Return, ReturnTable, ReturnRow
from wildlifecompliance.components.returns.utils_schema import Schema
from wildlifecompliance.utils import excel
import ast


# def _is_post_data_valid(ret, tables_info, post_data):

#     table_rows = _get_table_rows_from_post(tables_info['name'], post_data)
#     schema = Schema(ret.return_type.get_schema_by_name(tables_info['name']))
#     print("=========from is post data valid")
#     print(table_rows)
#     # print(schema)

#     for table in tables_info:
#         print(table)
#         # print(table['name'])
#         # table_rows = _get_table_rows_from_post(table.get('name'), post_data)
#         # if len(table_rows) == 0:
#         #     return False
#         # schema = Schema(ret.return_type.get_schema_by_name(table.get('name')))
#         # if not schema.is_all_valid(table_rows):
#         #     return False
#     return True
def _is_post_data_valid(ret, tables_info, post_data):
    print(type(tables_info))
    print(tables_info)

    print("from utils===================")
    # print(ast.literal_eval(table))

    table_rows = _get_table_rows_from_post(tables_info, post_data)
    print("=======printing table rows=====")
    print(table_rows)
    if len(table_rows) == 0:
        return False
    schema = Schema(ret.return_type.get_schema_by_name(tables_info))
    print("===========Schema Info========")
    print(schema.is_all_valid(table_rows))
    if not schema.is_all_valid(table_rows):
        return False
    return True


def _get_table_rows_from_post(table_name, post_data):
    table_namespace = table_name + '::'
    by_column = dict([(key.replace(table_namespace, ''), post_data.getlist(
        key)) for key in post_data.keys() if key.startswith(table_namespace)])
    # by_column is of format {'col_header':[row1_val, row2_val,...],...}
    num_rows = len(
        list(
            by_column.values())[0]) if len(
        by_column.values()) > 0 else 0
    rows = []
    for row_num in range(num_rows):
        row_data = {}
        for key, value in by_column.items():
            row_data[key] = value[row_num]
        # filter empty rows.
        is_empty = True
        for value in row_data.values():
            if len(value.strip()) > 0:
                is_empty = False
                break
        if not is_empty:
            rows.append(row_data)
    return rows


def _create_return_data_from_post_data(ret, tables_info, post_data):
    rows = _get_table_rows_from_post(tables_info, post_data)
    if rows:
        return_table = ReturnTable.objects.get_or_create(
            name=tables_info, ret=ret)[0]
        # delete any existing rows as they will all be recreated
        return_table.returnrow_set.all().delete()
        return_rows = [
            ReturnRow(
                return_table=return_table,
                data=row) for row in rows]
        ReturnRow.objects.bulk_create(return_rows)


class SpreadSheet(object):
    """
    An utility object for Excel manipulation.
    """

    def __init__(self, _return, _filename):
        self.ret = _return
        self.filename = _filename
        self.errors = []
        self.rows_list = []

    def factory(self):
        """
        Simple Factory Method for spreadsheet types.
        :return: Specialised SpreadSheet.
        """
        if self.filename.name == 'regulation15.xlsx':
            return Regulation15Sheet(self.ret, self.filename)

    def get_table_rows(self):
        """
        Gets the row of data.
        :return: list format {'col_header':[row1_val,, row2_val,...],...}
        """
        wb = excel.load_workbook(self.filename)
        sheet_name = excel.get_sheet_titles(wb)[0]
        ws = wb[sheet_name]
        table_data = excel.TableData(ws, 1, 1)
        row_list = table_data._parse_rows()
        num_rows = row_list.__len__()
        for row_num in range(num_rows):
            row_data = {}
            for key, value in table_data.by_columns():
                row_data[key] = value[row_num] if value[row_num] is not None else ''
            self.rows_list.append(row_data)

        return self.rows_list

    def create_return_data(self):
        """
        Method to persist Return record.
        :return: Boolean
        """
        return False

    def is_valid(self):
        """
        Validates against schema.
        :return: Boolean
        """
        return False

    def get_error(self):
        """
        List of errors.
        :return:
        """

        return self.errors


class Regulation15Sheet(SpreadSheet):
    """
    Specialised utility object for Regulation 15 Spreadsheet.
    """
    REGULATION_15 = 'regulation-15'

    def __init__(self, _ret, _filename):
        super(Regulation15Sheet, self).__init__(_ret, _filename)
        self.schema = Schema(
            self.ret.return_type.get_schema_by_name(
                self.REGULATION_15))

    def is_valid(self):
        """
        Validates against schema.
        :return: Boolean
        """
        table_rows = self.get_table_rows()
        if len(table_rows) == 0:
            return False
        for row in table_rows:
            self.errors.append(self.schema.get_error_fields(row))

        return self.errors.__len__() == 0

    def create_return_data(self):
        """
        Method to persist Return record.
        :return:
        """
        if self.rows_list:
            return_table = ReturnTable.objects.get_or_create(
                name=self.REGULATION_15, ret=self.ret)[0]
            # delete any existing rows as they will all be recreated
            return_table.returnrow_set.all().delete()
            return_rows = [
                ReturnRow(
                    return_table=return_table,
                    data=row) for row in self.rows_list]
            ReturnRow.objects.bulk_create(return_rows)

        return True
