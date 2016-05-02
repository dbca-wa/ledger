import os
import shutil

from preserialize.serialize import serialize

from models import Application, AmendmentRequest, Assessment, AssessmentCondition


PROCESSING_STATUSES = dict(Application.PROCESSING_STATUS_CHOICES)
ID_CHECK_STATUSES = dict(Application.ID_CHECK_STATUS_CHOICES)
CHARACTER_CHECK_STATUSES = dict(Application.CHARACTER_CHECK_STATUS_CHOICES)
REVIEW_STATUSES = dict(Application.REVIEW_STATUS_CHOICES)
AMENDMENT_REQUEST_REASONS = dict(AmendmentRequest.REASON_CHOICES)
ASSESSMENT_STATUSES = dict(Assessment.STATUS_CHOICES)
ASSESSMENT_CONDITION_ACCEPTANCE_STATUSES = dict(AssessmentCondition.ACCEPTANCE_STATUS_CHOICES)


def create_data_from_form(form_structure, post_data, file_data, post_data_index=None):
    data = {}

    for item in form_structure:
        data.update(_create_data_from_item(item, post_data, file_data, post_data_index))

    return data


def _create_data_from_item(item, post_data, file_data, post_data_index=None):
    item_data = {}

    if 'name' in item and item.get('type', '') != 'group':
        if item.get('type', '') == 'declaration':
            if post_data_index is not None:
                post_data_list = post_data.getlist(item['name'])
                if len(post_data_list) > 0:
                    item_data[item['name']] = post_data_list[post_data_index]
                else:
                    item_data[item['name']] = False
            else:
                item_data[item['name']] = post_data.get(item['name'], 'off') == 'on'
        elif item.get('type', '') == 'file':
            if item['name'] in file_data:
                item_data[item['name']] = str(file_data.get(item['name']))
            elif item['name'] + '-existing' in post_data and len(post_data[item['name'] + '-existing']) > 0:
                    item_data[item['name']] = post_data.get(item['name'] + '-existing')
            else:
                item_data[item['name']] = ''
        else:
            post_data_list = post_data.getlist(item['name'])
            if post_data_index is not None and len(post_data_list) > 0:
                item_data[item['name']] = post_data_list[post_data_index]
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
                    group_data.update(_create_data_from_item(child, post_data, file_data, group_index))
                groups.append(group_data)
            item_data[item['name']] = groups
        else:
            for child in item['children']:
                item_data.update(_create_data_from_item(child, post_data, file_data, post_data_index))

    return item_data


def get_all_filenames_from_application_data(item, data):
    filenames = []
    if item.get('type', '') == 'file':
        if item['name'] in data and len(data[item['name']]) > 0:
            filenames.append(data[item['name']])

    if 'children' in item:
        for child in item['children']:
            if child.get('type', '') == 'group':
                for child_data in data[child['name']]:
                    filenames += get_all_filenames_from_application_data(child, child_data)
            else:
                filenames += get_all_filenames_from_application_data(child, data)

    return filenames


def delete_application_session_data(session):
    if 'application' in session:
        if 'files' in session['application']:
            if os.path.exists(session.get('application').get('files')):
                try:
                    shutil.rmtree(session.get('application').get('files'))
                except:
                    pass

        del session['application']


def format_application(instance, attrs):
    attrs['processing_status'] = PROCESSING_STATUSES[attrs['processing_status']]
    attrs['id_check_status'] = ID_CHECK_STATUSES[attrs['id_check_status']]
    attrs['character_check_status'] = CHARACTER_CHECK_STATUSES[attrs['character_check_status']]
    attrs['review_status'] = REVIEW_STATUSES[attrs['review_status']]

    attrs['conditions'] = serialize([ap.condition for ap in instance.applicationcondition_set.all().order_by('order')])

    return attrs


def format_amendment_request(instance, attrs):
    attrs['reason'] = AMENDMENT_REQUEST_REASONS[attrs['reason']]

    return attrs


def format_assessment(instance, attrs):
    attrs['conditions'] = serialize(instance.assessmentcondition_set.all().order_by('order'),
                                    fields=['acceptance_status', 'id', 'condition'], posthook=format_assessment_condition)
    attrs['status'] = ASSESSMENT_STATUSES[attrs['status']]

    return attrs


def format_assessment_condition(instance, attrs):
    attrs['acceptance_status'] = ASSESSMENT_CONDITION_ACCEPTANCE_STATUSES[attrs['acceptance_status']]

    return attrs
