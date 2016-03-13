def create_data_from_form(item, post_data, post_data_index=None):
    item_data = {}

    if 'name' in item and item.get('type', '') != 'group':
        if item.get('type', '') == 'checkbox_field':
            if post_data_index is not None:
                post_data_list = post_data.getlist(item['name'])
                if len(post_data_list) > 0:
                    item_data[item['name']] = post_data_list[post_data_index]
                else:
                    item_data[item['name']] = False
            else:
                item_data[item['name']] = post_data.get(item['name'], 'off') == 'on'
        else:
            if post_data_index is not None:
                item_data[item['name']] = post_data.getlist(item['name'])[post_data_index]
            else:
                item_data[item['name']] = post_data.get(item['name'])

    if 'children' in item:
        if item.get('type', '') == 'group':
            # check how many groups there are
            num_groups = 0
            for group_item in item.get('children'):
                if group_item['type'] != 'section' and group_item['type'] != 'group':
                    num_groups = len(post_data.getlist(group_item['name']))
                    break

            groups = []
            for group_index in range(0, num_groups): 
                group_data = {}
                for child in item['children']:
                    group_data.update(create_data_from_form(child, post_data, group_index))
                groups.append(group_data)
            item_data[item['name']] = groups
        else:
            for child in item['children']:
                item_data.update(create_data_from_form(child, post_data))

    return item_data
