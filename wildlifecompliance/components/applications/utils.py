import re
from datetime import datetime
from django.db import transaction
from preserialize.serialize import serialize
from ledger.accounts.models import EmailUser, Document
from wildlifecompliance.components.applications.models import ApplicationDocument
from wildlifecompliance.components.applications.serializers import SaveApplicationSerializer
import json
from wildlifecompliance.components.licences.models import WildlifeLicenceActivity, DefaultActivity, WildlifeLicenceActivityType, DefaultActivityType
from wildlifecompliance.utils.assess_utils import create_app_activity_type_model, create_licence, pdflatex, get_activity_type_sys_answers
import traceback


def create_data_from_form(
        schema,
        post_data,
        file_data,
        post_data_index=None,
        special_fields=[],
        assessor_data=False):
    data = {}
    special_fields_list = []
    assessor_data_list = []
    comment_data_list = {}
    special_fields_search = SpecialFieldsSearch(special_fields)
    if assessor_data:
        assessor_fields_search = AssessorDataSearch()
        comment_fields_search = CommentDataSearch()
    try:
        for item in schema:
            data.update(
                _create_data_from_item(
                    item,
                    post_data,
                    file_data,
                    0,
                    ''))
            special_fields_search.extract_special_fields(
                item, post_data, file_data, 0, '')
            if assessor_data:
                assessor_fields_search.extract_special_fields(
                    item, post_data, file_data, 0, '')
                comment_fields_search.extract_special_fields(
                    item, post_data, file_data, 0, '')
        special_fields_list = special_fields_search.special_fields
        if assessor_data:
            assessor_data_list = assessor_fields_search.assessor_data
            comment_data_list = comment_fields_search.comment_data
    except BaseException:
        traceback.print_exc()
    if assessor_data:
        return [data], special_fields_list, assessor_data_list, comment_data_list

    return [data], special_fields_list


def _extend_item_name(name, suffix, repetition):
    return '{}{}-{}'.format(name, suffix, repetition)


def _create_data_from_item(item, post_data, file_data, repetition, suffix):
    item_data = {}

    if 'name' in item:
        extended_item_name = item['name']
    else:
        raise Exception('Missing name in item %s' % item['label'])

    if 'children' not in item:
        if item['type'] in ['checkbox' 'declaration']:
            #item_data[item['name']] = post_data[item['name']]
            item_data[item['name']] = extended_item_name in post_data
        elif item['type'] == 'file':
            if extended_item_name in file_data:
                item_data[item['name']] = str(
                    file_data.get(extended_item_name))
                # TODO save the file here
            elif extended_item_name + '-existing' in post_data and len(post_data[extended_item_name + '-existing']) > 0:
                item_data[item['name']] = post_data.get(
                    extended_item_name + '-existing')
            else:
                item_data[item['name']] = ''
        else:
            if extended_item_name in post_data:
                if item['type'] == 'multi-select':
                    item_data[item['name']] = post_data.getlist(
                        extended_item_name)
                else:
                    item_data[item['name']] = post_data.get(extended_item_name)
    else:
        if 'repetition' in item:
            item_data = generate_item_data(extended_item_name,
                                           item,
                                           item_data,
                                           post_data,
                                           file_data,
                                           len(post_data[item['name']]),
                                           suffix)
        else:
            item_data = generate_item_data(
                extended_item_name,
                item,
                item_data,
                post_data,
                file_data,
                1,
                suffix)

    if 'conditions' in item:
        for condition in item['conditions'].keys():
            for child in item['conditions'][condition]:
                # print(child)
                item_data.update(
                    _create_data_from_item(
                        child,
                        post_data,
                        file_data,
                        repetition,
                        suffix))

    return item_data


def generate_item_data(
        item_name,
        item,
        item_data,
        post_data,
        file_data,
        repetition,
        suffix):
    item_data_list = []
    for rep in xrange(0, repetition):
        child_data = {}
        for child_item in item.get('children'):
            # print(child_item)
            child_data.update(_create_data_from_item(
                child_item, post_data, file_data, 0, '{}-{}'.format(suffix, rep)))
        item_data_list.append(child_data)

        item_data[item['name']] = item_data_list
    return item_data


class AssessorDataSearch(object):

    def __init__(self, lookup_field='canBeEditedByAssessor'):
        self.lookup_field = lookup_field
        self.assessor_data = []

    def extract_assessor_data(self, item, post_data):
        values = []
        res = {
            'name': item,
            'assessor': '',
            'assessments': []
        }
        for k in post_data:
            if re.match(item, k):
                values.append({k: post_data[k]})
        if values:
            for v in values:
                for k, v in v.items():
                    parts = k.split('{}-'.format(item))
                    if len(parts) > 1:
                        # split parts to see if assessment
                        ref_parts = parts[1].split('Assessment-')
                        if len(ref_parts) > 1:
                            # Assessments
                            res['assessments'].append({
                                'value': v,
                                'email': ref_parts[1],
                                'full_name': EmailUser.objects.get(email=ref_parts[1]).get_full_name()
                            })
                        else:
                            # Assessor
                            res['assessor'] = v

        return res

    def extract_special_fields(
            self,
            item,
            post_data,
            file_data,
            repetition,
            suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            if item.get(self.lookup_field):
                self.assessor_data.append(
                    self.extract_assessor_data(
                        extended_item_name, post_data))

        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, len(post_data[item['name']]), suffix)
            else:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, 1, suffix)

        if 'conditions' in item:
            for condition in item['conditions'].keys():
                for child in item['conditions'][condition]:
                    item_data.update(
                        self.extract_special_fields(
                            child,
                            post_data,
                            file_data,
                            repetition,
                            suffix))

        return item_data

    def generate_item_data_special_field(
            self,
            item_name,
            item,
            item_data,
            post_data,
            file_data,
            repetition,
            suffix):
        item_data_list = []
        for rep in xrange(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(
                    child_item, post_data, file_data, 0, '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data


class CommentDataSearch(object):

    def __init__(self, lookup_field='canBeEditedByAssessor'):
        self.lookup_field = lookup_field
        self.comment_data = {}

    def extract_comment_data(self, item, post_data):
        res = {}
        values = []
        for k in post_data:
            if re.match(item, k):
                values.append({k: post_data[k]})
        if values:
            for v in values:
                for k, v in v.items():
                    parts = k.split('{}'.format(item))
                    if len(parts) > 1:
                        ref_parts = parts[1].split('-comment-field')
                        if len(ref_parts) > 1:
                            res = {'{}'.format(item): v}
        return res

    def extract_special_fields(
            self,
            item,
            post_data,
            file_data,
            repetition,
            suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            self.comment_data.update(
                self.extract_comment_data(
                    extended_item_name, post_data))

        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, len(post_data[item['name']]), suffix)
            else:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, 1, suffix)

        if 'conditions' in item:
            for condition in item['conditions'].keys():
                for child in item['conditions'][condition]:
                    item_data.update(
                        self.extract_special_fields(
                            child,
                            post_data,
                            file_data,
                            repetition,
                            suffix))

        return item_data

    def generate_item_data_special_field(
            self,
            item_name,
            item,
            item_data,
            post_data,
            file_data,
            repetition,
            suffix):
        item_data_list = []
        for rep in xrange(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(
                    child_item, post_data, file_data, 0, '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data


class SpecialFieldsSearch(object):

    def __init__(self, lookable_fields):
        self.lookable_fields = lookable_fields
        self.special_fields = {}

    def extract_special_fields(
            self,
            item,
            post_data,
            file_data,
            repetition,
            suffix):
        item_data = {}
        if 'name' in item:
            extended_item_name = item['name']
        else:
            raise Exception('Missing name in item %s' % item['label'])

        if 'children' not in item:
            for f in self.lookable_fields:
                if item['type'] in ['checkbox' 'declaration']:
                    val = None
                    val = item.get(f, None)
                    if val:
                        item_data[f] = extended_item_name in post_data
                        self.special_fields.update(item_data)
                else:
                    if extended_item_name in post_data:
                        val = None
                        val = item.get(f, None)
                        if val:
                            if item['type'] == 'multi-select':
                                item_data[f] = ','.join(
                                    post_data.getlist(extended_item_name))
                            else:
                                item_data[f] = post_data.get(
                                    extended_item_name)
                            self.special_fields.update(item_data)
        else:
            if 'repetition' in item:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, len(post_data[item['name']]), suffix)
            else:
                item_data = self.generate_item_data_special_field(
                    extended_item_name, item, item_data, post_data, file_data, 1, suffix)

        if 'conditions' in item:
            for condition in item['conditions'].keys():
                for child in item['conditions'][condition]:
                    item_data.update(
                        self.extract_special_fields(
                            child,
                            post_data,
                            file_data,
                            repetition,
                            suffix))

        return item_data

    def generate_item_data_special_field(
            self,
            item_name,
            item,
            item_data,
            post_data,
            file_data,
            repetition,
            suffix):
        item_data_list = []
        for rep in xrange(0, repetition):
            child_data = {}
            for child_item in item.get('children'):
                child_data.update(self.extract_special_fields(
                    child_item, post_data, file_data, 0, '{}-{}'.format(suffix, rep)))
            item_data_list.append(child_data)

            item_data[item['name']] = item_data_list
        return item_data


def save_proponent_data(instance, request, viewset):
    with transaction.atomic():
        try:
            lookable_fields = [
                'isTitleColumnForDashboard',
                'isActivityColumnForDashboard',
                'isRegionColumnForDashboard']
            extracted_fields, special_fields = create_data_from_form(
                instance.schema, request.POST, request.FILES, special_fields=lookable_fields)
            instance.data = extracted_fields
            data = {
                'region': special_fields.get(
                    'isRegionColumnForDashboard',
                    None),
                'title': special_fields.get(
                    'isTitleColumnForDashboard',
                    None),
                'activity': special_fields.get(
                    'isActivityColumnForDashboard',
                    None),
                'data': extracted_fields,
                'processing_status': instance.PROCESSING_STATUS_CHOICES[1][0] if instance.processing_status == 'temp' else instance.processing_status,
                'customer_status': instance.PROCESSING_STATUS_CHOICES[1][0] if instance.processing_status == 'temp' else instance.customer_status,
            }
            serializer = SaveApplicationSerializer(
                instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            viewset.perform_update(serializer)

            # set the isEditable fields
            #import ipdb; ipdb.set_trace()
            for activity_type in instance.activity_types:
                if not activity_type.data or (activity_type.data and 'editable' not in activity_type.data[0]):
                    activity_type.data = [{'editable': get_activity_type_sys_answers(activity_type)}]
                    activity_type.save()

            # Save Documents
#            for f in request.FILES:
#                try:
#                    #document = instance.documents.get(name=str(request.FILES[f]))
#                    document = instance.documents.get(input_name=f)
#                except ApplicationDocument.DoesNotExist:
#                    document = instance.documents.get_or_create(input_name=f)[0]
#                document.name = str(request.FILES[f])
#                if document._file and os.path.isfile(document._file.path):
#                    os.remove(document._file.path)
#                document._file = request.FILES[f]
#                document.save()
            # End Save Documents
        except BaseException:
            raise


def save_assessor_data(instance, request, viewset):
    with transaction.atomic():
        try:
            lookable_fields = [
                'isTitleColumnForDashboard',
                'isActivityColumnForDashboard',
                'isRegionColumnForDashboard']
            extracted_fields, special_fields, assessor_data, comment_data = create_data_from_form(
                instance.schema, request.POST, request.FILES, special_fields=lookable_fields, assessor_data=True)
            data = {
                'data': extracted_fields,
                'assessor_data': assessor_data,
                'comment_data': comment_data,
            }
            serializer = SaveApplicationSerializer(
                instance, data, partial=True)
            serializer.is_valid(raise_exception=True)
            viewset.perform_update(serializer)
            # Save Documents
            for f in request.FILES:
                try:
                    #document = instance.documents.get(name=str(request.FILES[f]))
                    document = instance.documents.get(input_name=f)
                except ApplicationDocument.DoesNotExist:
                    document = instance.documents.get_or_create(input_name=f)[
                        0]
                document.name = str(request.FILES[f])
                if document._file and os.path.isfile(document._file.path):
                    os.remove(document._file.path)
                document._file = request.FILES[f]
                document.save()
            # End Save Documents
        except BaseException:
            raise

def save_assess_data(instance,request,viewset):

    if instance.processing_status == instance.PROCESSING_STATUS_DRAFT:
        return

    can_process = True if request.data.has_key('action') and request.data['action'] == 'process' else False

    def get_kv_pair(key_substring):
        # check if substring is part of dict key, and return key,value if so
        return [{key:value} for key, value in request.data.items() if key_substring in key]

    with transaction.atomic():
        try:
            #import ipdb; ipdb.set_trace()
            #instance.licences.all().last().licence_sequence
            new_app = True
            for activity_type in instance.activity_types:
                code = WildlifeLicenceActivity.objects.get(name=activity_type.activity_name).code.lower()
                activity_type.purpose = request.data[code + '_purpose']
                activity_type.additional_info = request.data[code + '_additional_info']
                if request.data.has_key(code + '_standard_advanced'):
                    activity_type.advanced = True if request.data[code + '_standard_advanced'] == 'on' else False
                else:
                    activity_type.advanced = False

                activity_type.conditions = request.data[code + '_conditions']
                activity_type.issue_date = datetime.strptime(request.data[code + '_issue_date'], "%d/%m/%Y") if request.data[code + '_issue_date'] else None
                activity_type.start_date = datetime.strptime(request.data[code + '_start_date'], "%d/%m/%Y") if request.data[code + '_start_date'] else None
                activity_type.expiry_date = datetime.strptime(request.data[code + '_expiry_date'], "%d/%m/%Y") if request.data[code + '_expiry_date'] else None
                if request.data.has_key(code + '_to_be_issued'):
                    activity_type.to_be_issued = True if request.data[code + '_to_be_issued'] == 'on' else False
                else:
                    activity_type.to_be_issued = False
                if request.data.has_key(code + '_processed'):
                    activity_type.processed = True if request.data[code + '_processed'] == 'on' else False
                else:
                    activity_type.processed = False

                # check if table exists and save possibly updated/overriden data
                element_types = ['_table_', '_text_area_', '_text_']
                for element_type in element_types:
                    for kv_pair in get_kv_pair(code + element_type):
                        for k,v in kv_pair.iteritems():
                            if not (element_type == '_text_' and 'text_area' in k): # hack to allow strip() to work below
                                name = k.strip(code + element_type)
                                if 'comment-field' not in name:
                                    #import ipdb; ipdb.set_trace()
                                    activity_type.data[0]['editable'][name]['answer'] = request.data[k]

#                for kv_pair in get_kv_pair(code+'_text_area_'):
#                    for k,v in kv_pair.iteritems():
#                        name = k.strip(code+'_text_area_')
#                        if 'comment-field' not in name:
#                            activity_type.data[0]['editable'][name]['answer'] = request.data[k]
#
#                for kv_pair in get_kv_pair(code+'_text_'):
#                    for k,v in kv_pair.iteritems():
#                        name = k.strip(code+'_text_')
#                        if 'comment-field' not in name:
#                            activity_type.data[0]['editable'][name]['answer'] = request.data[k]

                #import ipdb; ipdb.set_trace()
                if can_process and activity_type.to_be_issued and not activity_type.processed:
                    # create licences
                    activity_type.processed = True
                    if not activity_type.data:
                        activity_type.data = [add_editable_items(activity_type)]

                    create_licence(instance, activity_type.activity_name, new_app)
                    new_app = False

                #activity_type.data = [add_editable_items(activity_type)]
                activity_type.save()
                #import ipdb; ipdb.set_trace()

            if instance.licences.count() == instance.activity_types.count():
                instance.customer_status = 'accepted'
                instance.processing_status = 'approved'
            elif instance.licences.count() == 0:
                instance.customer_status = 'declined'
                instance.processing_status = 'declined'
            else:
                instance.customer_status = 'partially_accepted'
                instance.processing_status = 'partially_approved'

        except:
            raise

    #import ipdb; ipdb.set_trace()
    if can_process and instance.processing_status != 'declined':
        pdflatex(request, instance)

    return


def add_editable_items(activity_type):
    return {'editable': get_activity_type_sys_answers(activity_type)}


def get_activity_type_schema(activity_ids):
    schema_activity = []
    schema_tab = []

    try:
        activities = WildlifeLicenceActivity.objects.filter(
            id__in=activity_ids
        )
    except ValueError:
        return schema_tab
    unique_type_activities = activities.distinct('licence_activity_type')

    for index, activity in enumerate(unique_type_activities):
        activity_type = activity.licence_activity_type
        schema_activity = []
        activity_type_item = {}
        activity_type_item.update(
            {key: value for key, value in activity_type.__dict__.items()}
        )
        activity_type_item["name"] = activity_type.name
        activity_type_item["processing_status"] = "Draft"
        activity_type_item["proposed_decline"] = False

        for type_activity in activities.filter(licence_activity_type__id=activity_type.id):
            schema_activity += type_activity.schema

        update_schema_name(schema_activity, index)
        schema_tab.append({"type": "tab",
                           "id": activity_type.id,
                           "label": activity_type.name,
                           "name": activity_type.name,
                           "status": "Draft",
                           "children": schema_activity
                           })
    return schema_tab


def update_schema_name(item_data, id):

    for item in item_data:
        # print('name')
        item['name'] = item['name'] + '_' + str(id)
        # print(item['name'])
        if 'children' in item:
            update_schema_name(item['children'], id)
            # print(item['children'])
