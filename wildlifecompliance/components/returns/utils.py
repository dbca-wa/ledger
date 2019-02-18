from wildlifecompliance.components.returns.models import Return,ReturnTable,ReturnRow
from wildlifecompliance.components.returns.utils_schema import Schema
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
    by_column = dict([(key.replace(table_namespace, ''), post_data.getlist(key)) for key in post_data.keys() if
                      key.startswith(table_namespace)])
    # by_column is of format {'col_header':[row1_val, row2_val,...],...}
    num_rows = len(list(by_column.values())[0]) if len(by_column.values()) > 0 else 0
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
        return_table = ReturnTable.objects.get_or_create(name=tables_info, ret=ret)[0]
        # delete any existing rows as they will all be recreated
        return_table.returnrow_set.all().delete()
        return_rows = [ReturnRow(return_table=return_table, data=row) for row in rows]
        ReturnRow.objects.bulk_create(return_rows)