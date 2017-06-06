from preserialize.serialize import serialize
from ledger.accounts.models import EmailUser, Document

def extract_licence_fields(schema, data):
    licence_fields = []

    for item in schema:
        _extract_licence_fields_from_item(item, data, licence_fields)
    for f in licence_fields:
        for key in f:
            if type(f[key]) is list:
                concat = {}
                for c in f[key]:
                    concat.update(c)
                f[key] = [concat]
    return licence_fields

def _extract_licence_fields_from_item(item, data, licence_fields):
    children_extracted = False
    licence_field={}
    if 'section' != item['type']:
        # label / checkbox types are extracted differently so skip here
        if item['type'] not in ('label', 'checkbox'):
            licence_field[item['name']] = _extract_item_data(item['name'], data)
            licence_fields.append(licence_field)
    else:
        licence_field[item['name']] = []
        group_licence_fields = {}
        for child_item in item.get('children'):
            if child_item['type'] == 'label':
                _extract_label_and_checkboxes(child_item, item.get('children'), data)
            if child_item['type'] not in ('label','checkbox','select','radio'):
                group_licence_fields[child_item['name']] = _extract_item_data(child_item['name'], data)
            if 'conditions' in child_item:
                _extract_licence_fields_from_item(child_item,data,licence_field[item['name']])
        licence_field[item['name']].append(group_licence_fields)
        licence_fields.append(licence_field)
        children_extracted = True

    if 'conditions' in item:
        for condition in item['conditions'].keys():
            for child_item in item['conditions'][condition]:
                if child_item['type'] == 'label' and child_item.get('isCopiedToPermit', False):
                    _extract_label_and_checkboxes(child_item, item['conditions'][condition], data, licence_fields)
                _extract_licence_fields_from_item(child_item, data, licence_fields)

def _extract_label_and_checkboxes(current_item, items, data, licence_fields):
    licence_field = {}
    # find index of first checkbox after checkbox label within current item list
    checkbox_index = 0
    while checkbox_index < len(items) and items[checkbox_index]['name'] != current_item['name']:
        checkbox_index += 1
    checkbox_index += 1

    # add all checkboxes to licence field options
    while checkbox_index < len(items) and items[checkbox_index]['type'] == 'checkbox':
        name = items[checkbox_index]['name']
        option = {
            'name': name,
            'label': items[checkbox_index]['label']
        }
        if name in data:
            option['data'] = data[name]

        licence_field['options'] = option

        checkbox_index += 1

    licence_fields.append(licence_field)


def _create_licence_field(item):
    return {
        'name': item['name'],
        'type': item['type'],
        'label': item['licenceFieldLabel'] if 'licenceFieldLabel' in item else item['label'],
        'help_text': item.get('licenceFieldHelpText', ''),
        'readonly': item.get('isLicenceFieldReadonly', False)
    }


def _extract_item_data(name, data):
    def ___extract_item_data(name, data):
        if isinstance(data, dict):
            if name in data:
                return data[name]
            else:
                for value in data.values():
                    result = ___extract_item_data(name, value)
                    if result is not None:
                        return result
        if isinstance(data, list):
            for item in data:
                result = ___extract_item_data(name, item)
                if result is not None:
                    return result

    result = ___extract_item_data(name, data)

    return result if result is not None else ''


def update_licence_fields(licence_fields, post_data):
    for field in licence_fields:
        if 'children' not in field:
            if field['type'] == 'label':
                for option in field['options']:
                    if option['name'] in post_data:
                        option['data'] = post_data[option['name']]
            else:
                field['data'] = post_data.get(field['name'])
        else:
            for index, group in enumerate(field['children']):
                for child_field in group:
                    if child_field['type'] == 'label':
                        for option in child_field['options']:
                            if option['name'] in post_data:
                                data_list = post_data.getlist(option['name'])
                                if index < len(data_list):
                                    option['data'] = data_list[index]
                    else:
                        data_list = post_data.getlist(child_field['name'])
                        if index < len(data_list):
                            child_field['data'] = data_list[index]

    return licence_fields
